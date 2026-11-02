# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import json
from datetime import datetime
from unittest import mock

import requests
from odoo_test_helper import FakeModelLoader

from odoo import Command
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.component.tests.common import TransactionComponentRegistryCase
from odoo.addons.connector.exception import RetryableJobError


def wordpress_response(status_code, payload, headers=None):
    """A WordPress answer whose JSON body is ``payload``."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(payload).encode()
    response.headers.update(headers or {})
    return response


class FakeWordpressPosts:
    """Serves ``posts`` to GET requests a page at a time, with the total in
    the X-WP-Total header, as the WordPress REST API does, and keeps the
    query of each request."""

    def __init__(self, posts):
        self.posts = posts
        self.queries = []

    def get(self, url, params=None, auth=None, verify=None):
        # only what the adapter sends: a keyword left over would reach requests
        self.queries.append(dict(params))
        offset = params.get("offset", 0)
        page = self.posts[offset : offset + params["per_page"]]
        return wordpress_response(200, page, {"X-WP-Total": str(len(self.posts))})


class ConnectorExtensionWordpressTestAdapter(Component):
    _name = "connector.extension.wordpress.test.adapter"
    _inherit = "connector.extension.wordpress.adapter.crud"
    _apply_on = "res.partner"


class TestWordpressAdapter(TransactionComponentRegistryCase):
    """The WordPress adapter of partners, on a test backend loaded as a fake
    model. No call leaves the test: requests is patched in each one."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import (
            ConnectorExtensionWordpressTestBackend,
            ConnectorExtensionWordpressTestShopBackend,
            ConnectorExtensionWordpressTestStoreBackend,
        )

        fake_models = (
            ConnectorExtensionWordpressTestBackend,
            ConnectorExtensionWordpressTestShopBackend,
            ConnectorExtensionWordpressTestStoreBackend,
        )
        cls.loader.update_registry(fake_models)
        # Odoo's TransactionCase.check_attrs (odoo/tests/common.py) fails each
        # test after which a model class has an attribute its attrs_before entry
        # does not list. TransactionCase.setUpClass fills attrs_before before
        # the fake models exist: their entries are the attributes they have once
        # loaded.
        for fake_model in fake_models:
            cls.attrs_before[fake_model._name] = cls.attrs_before["base"] | set(
                vars(cls.registry[fake_model._name])
            )
        cls._setup_registry(cls)
        cls.comp_registry.load_components("connector_extension_wordpress")
        cls._build_components(cls, ConnectorExtensionWordpressTestAdapter)
        cls.backend = cls.env["connector.extension.wordpress.test.backend"].create(
            {
                "name": "WordPress Test",
                "lang_ids": [Command.set(cls.env.ref("base.lang_en").ids)],
                "url": "https://wordpress.example.com",
                "username": "wp_user_test",
                "application_password": "app_password_test",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls._teardown_registry(cls)
        cls.loader.restore_registry()
        super().tearDownClass()

    def adapter(self, backend=None):
        """The adapter of partners on ``backend``, by default the WordPress
        test backend."""
        with (backend if backend is not None else self.backend).work_on(
            "res.partner", components_registry=self.comp_registry
        ) as work:
            return work.component(usage="adapter")

    def test_calls_reach_the_rest_api_with_the_backend_credentials(self):
        self.backend.verify_ssl = False
        answer = wordpress_response(200, {"environment": {"version": "6.5"}})
        with mock.patch.object(requests, "get", return_value=answer) as get:
            self.adapter()._exec("get", "system_status")
        get.assert_called_once_with(
            "https://wordpress.example.com/wp-json/wp/v2/system_status",
            auth=("wp_user_test", "app_password_test"),
            verify=False,
        )

    def test_system_status_returns_the_whole_answer(self):
        answer = wordpress_response(
            200,
            {"environment": {"version": "6.5"}},
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )
        with mock.patch.object(requests, "get", return_value=answer):
            status = self.adapter()._exec("get", "system_status")
        self.assertEqual(
            status,
            {
                "ok": True,
                "status_code": 200,
                "headers": {"Content-Type": "application/json; charset=UTF-8"},
                "data": {"environment": {"version": "6.5"}},
            },
        )

    def test_get_reads_every_page_up_to_the_total(self):
        self.backend.page_size = 2
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts")
        self.assertEqual(posts, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(
            wordpress.queries,
            [
                {"per_page": 1},
                {"offset": 0, "per_page": 2},
                {"offset": 2, "per_page": 1},
            ],
        )

    def test_get_stops_at_an_empty_page_before_the_total(self):
        self.backend.page_size = 2
        answers = [
            wordpress_response(200, [{"id": 1}], {"X-WP-Total": "3"}),
            wordpress_response(200, [{"id": 1}, {"id": 2}]),
            wordpress_response(200, []),
            AssertionError("a page was asked for after an empty one"),
        ]
        with mock.patch.object(requests, "get", side_effect=answers) as get:
            posts = self.adapter()._exec("get", "posts")
        self.assertEqual(posts, [{"id": 1}, {"id": 2}])
        self.assertEqual(get.call_count, 3)

    def test_get_with_a_limit_reads_without_counting(self):
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", limit=2)
        self.assertEqual(posts, [{"id": 1}, {"id": 2}])
        self.assertEqual(wordpress.queries, [{"offset": 0, "per_page": 2}])

    def test_get_starts_at_the_offset_of_the_domain(self):
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec(
                "get", "posts", domain=[("offset", "=", 1)], limit=2
            )
        self.assertEqual(posts, [{"id": 2}, {"id": 3}])
        self.assertEqual(wordpress.queries, [{"offset": 1, "per_page": 2}])

    def test_get_starts_at_the_offset_argument(self):
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get) as get:
            posts = self.adapter()._exec("get", "posts", offset=1, limit=2)
        self.assertEqual(posts, [{"id": 2}, {"id": 3}])
        self.assertEqual(wordpress.queries, [{"offset": 1, "per_page": 2}])
        self.assertNotIn("offset", get.call_args.kwargs)

    def test_get_prefers_the_offset_of_the_domain_to_the_argument(self):
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get) as get:
            posts = self.adapter()._exec(
                "get", "posts", domain=[("offset", "=", 1)], offset=2, limit=2
            )
        self.assertEqual(posts, [{"id": 2}, {"id": 3}])
        self.assertNotIn("offset", get.call_args.kwargs)

    def test_get_reads_pages_of_the_size_of_the_domain(self):
        # the domain's page size wins over the backend's, larger here
        self.backend.page_size = 5
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", domain=[("per_page", "=", 2)])
        self.assertEqual(posts, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(
            wordpress.queries,
            [
                {"per_page": 1},
                {"offset": 0, "per_page": 2},
                {"offset": 2, "per_page": 1},
            ],
        )

    def test_get_without_a_page_size_reads_pages_of_100(self):
        self.backend.page_size = 0
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", limit=150)
        self.assertEqual(posts, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(
            wordpress.queries,
            [{"offset": 0, "per_page": 100}, {"offset": 3, "per_page": 100}],
        )

    def test_get_with_a_negative_page_size_reads_pages_of_100(self):
        self.backend.page_size = -1
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", limit=150)
        self.assertEqual(posts, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(
            wordpress.queries,
            [{"offset": 0, "per_page": 100}, {"offset": 3, "per_page": 100}],
        )

    def test_get_without_a_page_size_stops_at_the_limit(self):
        self.backend.page_size = 0
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", limit=2)
        self.assertEqual(posts, [{"id": 1}, {"id": 2}])
        self.assertEqual(wordpress.queries, [{"offset": 0, "per_page": 2}])

    def test_get_sends_the_search_fields_and_filters_the_rest_here(self):
        wordpress = FakeWordpressPosts(
            [{"id": 1, "status": "publish"}, {"id": 2, "status": "draft"}]
        )
        domain = [
            ("modified_after", "=", datetime(2026, 1, 15, 8, 0)),
            ("status", "=", "publish"),
        ]
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            posts = self.adapter()._exec("get", "posts", domain=domain)
        self.assertEqual(posts, [{"id": 1, "status": "publish"}])
        self.assertEqual(
            wordpress.queries,
            [
                {"modified_after": "2026-01-15T08:00:00Z", "per_page": 1},
                {"modified_after": "2026-01-15T08:00:00Z", "offset": 0, "per_page": 2},
            ],
        )

    def test_total_items_without_a_domain_count_every_post(self):
        wordpress = FakeWordpressPosts([{"id": 1}, {"id": 2}, {"id": 3}])
        with mock.patch.object(requests, "get", side_effect=wordpress.get):
            total = self.adapter().get_total_items("posts")
        self.assertEqual(total, 3)
        self.assertEqual(wordpress.queries, [{"per_page": 1}])

    def test_version_names_the_wordpress_site(self):
        settings = wordpress_response(200, {"title": "Test Site"})
        with mock.patch.object(requests, "get", return_value=settings):
            version = self.adapter().get_version()
        self.assertEqual(version, "Wordpress 'Test Site' connected")

    def test_version_of_a_site_without_title_is_not_connected(self):
        settings = wordpress_response(200, {"title": ""})
        with mock.patch.object(requests, "get", return_value=settings):
            with self.assertRaisesRegex(ValidationError, "Wordpress not connected"):
                self.adapter().get_version()

    def test_post_sends_the_payload_and_returns_the_answer(self):
        answer = wordpress_response(201, {"id": 15})
        with mock.patch.object(requests, "post", return_value=answer) as post:
            created = self.adapter()._exec(
                "post",
                "media",
                data={
                    "headers": {"Content-Disposition": "attachment; filename=a.png"},
                    "data": b"image bytes",
                    "title": "Photo",
                },
            )
        self.assertEqual(created, {"id": 15})
        post.assert_called_once_with(
            "https://wordpress.example.com/wp-json/wp/v2/media",
            data=b"image bytes",
            params={"title": "Photo"},
            headers={"Content-Disposition": "attachment; filename=a.png"},
            auth=("wp_user_test", "app_password_test"),
            verify=True,
        )

    def test_put_sends_the_payload_and_returns_the_answer(self):
        answer = wordpress_response(200, {"id": 15, "title": "Photo"})
        with mock.patch.object(requests, "put", return_value=answer) as put:
            updated = self.adapter()._exec(
                "put", "media/15", data={"data": {"title": "Photo"}}
            )
        self.assertEqual(updated, {"id": 15, "title": "Photo"})
        put.assert_called_once_with(
            "https://wordpress.example.com/wp-json/wp/v2/media/15",
            data={"title": "Photo"},
            params={},
            headers={},
            auth=("wp_user_test", "app_password_test"),
            verify=True,
        )

    def test_post_uses_the_credentials_of_the_linked_wordpress(self):
        shop = self.env["connector.extension.wordpress.test.shop.backend"].create(
            {
                "name": "Shop Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://shop.example.com",
                "username": "shop_user_test",
                "application_password": "shop_password_test",
                "wordpress_backend_id": self.backend.id,
            }
        )
        answer = wordpress_response(201, {"id": 15})
        with mock.patch.object(requests, "post", return_value=answer) as post:
            self.adapter(shop)._exec("post", "media", data={"data": b"bytes"})
        self.assertEqual(
            post.call_args.kwargs["auth"], ("wp_user_test", "app_password_test")
        )

    def test_put_uses_the_credentials_of_the_linked_wordpress(self):
        shop = self.env["connector.extension.wordpress.test.shop.backend"].create(
            {
                "name": "Shop Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://shop.example.com",
                "username": "shop_user_test",
                "application_password": "shop_password_test",
                "wordpress_backend_id": self.backend.id,
            }
        )
        answer = wordpress_response(200, {"id": 15})
        with mock.patch.object(requests, "put", return_value=answer) as put:
            self.adapter(shop)._exec("put", "media/15", data={"data": b"bytes"})
        self.assertEqual(
            put.call_args.kwargs["auth"], ("wp_user_test", "app_password_test")
        )

    def test_post_without_a_linked_wordpress_uses_its_own_credentials(self):
        shop = self.env["connector.extension.wordpress.test.shop.backend"].create(
            {
                "name": "Shop Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://shop.example.com",
                "username": "shop_user_test",
                "application_password": "shop_password_test",
            }
        )
        answer = wordpress_response(201, {"id": 15})
        with mock.patch.object(requests, "post", return_value=answer) as post:
            self.adapter(shop)._exec("post", "media", data={"data": b"bytes"})
        self.assertEqual(
            post.call_args.kwargs["auth"], ("shop_user_test", "shop_password_test")
        )

    def test_put_without_a_linked_wordpress_uses_its_own_credentials(self):
        shop = self.env["connector.extension.wordpress.test.shop.backend"].create(
            {
                "name": "Shop Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://shop.example.com",
                "username": "shop_user_test",
                "application_password": "shop_password_test",
            }
        )
        answer = wordpress_response(200, {"id": 15})
        with mock.patch.object(requests, "put", return_value=answer) as put:
            self.adapter(shop)._exec("put", "media/15", data={"data": b"bytes"})
        self.assertEqual(
            put.call_args.kwargs["auth"], ("shop_user_test", "shop_password_test")
        )

    def test_post_without_credentials_of_its_own_uses_the_linked_ones(self):
        store = self.env["connector.extension.wordpress.test.store.backend"].create(
            {
                "name": "Store Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://store.example.com",
                "wordpress_backend_id": self.backend.id,
            }
        )
        answer = wordpress_response(201, {"id": 15})
        with mock.patch.object(requests, "post", return_value=answer) as post:
            self.adapter(store)._exec("post", "media", data={"data": b"bytes"})
        self.assertEqual(
            post.call_args.kwargs["auth"], ("wp_user_test", "app_password_test")
        )

    def test_post_without_credentials_nor_a_linked_wordpress_is_refused(self):
        store = self.env["connector.extension.wordpress.test.store.backend"].create(
            {
                "name": "Store Test",
                "lang_ids": [Command.set(self.env.ref("base.lang_en").ids)],
                "url": "https://store.example.com",
            }
        )
        with mock.patch.object(requests, "post") as post:
            with self.assertRaisesRegex(
                ValidationError,
                "The backend Store Test cannot call WordPress until a WordPress "
                "backend is chosen on it",
            ):
                self.adapter(store)._exec("post", "media", data={"data": b"bytes"})
        post.assert_not_called()

    def test_delete_is_not_supported(self):
        with self.assertRaises(NotImplementedError):
            self.adapter()._exec("delete", "posts/15")

    def test_options_is_not_supported(self):
        with self.assertRaises(NotImplementedError):
            self.adapter()._exec("options", "posts")

    def test_a_removed_post_suggests_removing_its_binding(self):
        answer = wordpress_response(
            404, {"code": "rest_post_invalid_id", "message": "Invalid post ID."}
        )
        with mock.patch.object(requests, "put", return_value=answer):
            with self.assertRaisesRegex(
                ValidationError,
                r"Invalid post ID\..* posts/15 has been removed from WordPress"
                r".*binding of the res\.partner",
            ):
                self.adapter()._exec("put", "posts/15", data={"data": {"title": "A"}})

    def test_a_rejected_upload_points_to_the_document(self):
        answer = wordpress_response(
            500,
            {
                "code": "rest_upload_sideload_error",
                "message": "Sorry, this file type is not permitted.",
            },
        )
        headers = {"Content-Disposition": "attachment; filename=a.png"}
        with mock.patch.object(requests, "post", return_value=answer):
            with self.assertRaisesRegex(
                ValidationError,
                r"file type is not permitted.*bad format.*filename=a\.png",
            ):
                self.adapter()._exec(
                    "post", "media", data={"headers": headers, "data": b"bytes"}
                )

    def test_other_errors_report_the_answer_and_the_resource(self):
        answer = wordpress_response(
            400, {"code": "rest_invalid_param", "message": "Invalid parameter(s)."}
        )
        with mock.patch.object(requests, "get", return_value=answer):
            with self.assertRaisesRegex(
                ValidationError, r"rest_invalid_param.*Resource: posts"
            ):
                self.adapter()._exec("get", "posts", limit=1)

    def test_an_error_is_returned_as_text_when_not_raising(self):
        answer = wordpress_response(400, {"code": "rest_invalid_param"})
        message = self.adapter()._manage_error_codes(
            "get", answer.json(), answer, "posts", raise_on_error=False
        )
        self.assertEqual(
            message, "Error: {'code': 'rest_invalid_param'}, Resource: posts"
        )

    def test_an_unreachable_site_is_retried_later(self):
        refused = requests.exceptions.ConnectionError("Connection refused")
        with mock.patch.object(requests, "get", side_effect=refused):
            with self.assertRaises(RetryableJobError):
                self.adapter()._exec("get", "system_status")

    def test_an_answer_that_is_not_json_is_reported_with_its_text(self):
        answer = requests.Response()
        answer.status_code = 200
        answer._content = b"<html>Site under maintenance</html>"
        with mock.patch.object(requests, "get", return_value=answer):
            with self.assertRaisesRegex(
                ValidationError,
                r"(?s)Error decoding json WordPress response.*Site under maintenance",
            ):
                self.adapter()._exec("get", "system_status")

    def test_an_error_answer_that_is_not_json_is_reported_with_its_text(self):
        answer = requests.Response()
        answer.status_code = 502
        answer._content = b"<html>Bad gateway</html>"
        with mock.patch.object(requests, "get", return_value=answer):
            with self.assertRaisesRegex(
                ValidationError,
                r"(?s)Error decoding json WordPress response.*Bad gateway",
            ):
                self.adapter()._exec("get", "system_status")
