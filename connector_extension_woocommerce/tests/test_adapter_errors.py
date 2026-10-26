# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from unittest.mock import Mock

import requests

from odoo.exceptions import ValidationError

from odoo.addons.connector.exception import RetryableJobError

from .common import WooCommerceAdapterCase


class TestAdapterErrors(WooCommerceAdapterCase):
    def test_get_of_a_route_woocommerce_does_not_have_explains_what_to_do(self):
        response = Mock(ok=False, status_code=404)
        response.json.return_value = {
            "code": "rest_no_route",
            "message": "No route was found matching the URL and request method.",
            "data": {"status": 404},
        }
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("get", "products/5/variations/9")
        self.assertEqual(
            error.exception.args[0],
            "Error: 'No route was found matching the URL and request method.'. "
            "Probably the products/5/variations/9 has been removed from "
            "Woocommerce. If it's the case, try to remove the binding of the "
            "res.partner.",
        )

    def test_create_of_a_term_that_exists_points_at_the_existing_one(self):
        response = Mock(ok=False, status_code=400)
        response.json.return_value = {
            "code": "term_exists",
            "message": "A term with the name provided already exists with this parent.",
            "data": {"status": 400, "resource_id": 57},
        }
        self.adapter.wcapi = Mock(post=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec(
                "post", "products/attributes/3/terms", data={"name": "Red"}
            )
        self.assertEqual(
            error.exception.args[0],
            "Error: 'A term with the name provided already exists with this "
            "parent.'. Probably repeated record already exists in Woocommerce. If "
            "you don't see it from the interface probably the database is dirty "
            "and you should check the database directly. It means that there's "
            "terms (value attributes) in table wp_term_taxonomy with a "
            "non-existent taxonomy (attribute).\nPlease, review the data in "
            "products/attributes/3/terms/57 and compare it with {'name': 'Red'}",
        )

    def test_update_refused_by_woocommerce_shows_its_answer_and_the_call(self):
        response = Mock(ok=False, status_code=401)
        response.json.return_value = {
            "code": "woocommerce_rest_cannot_edit",
            "message": "Sorry, you are not allowed to edit this resource.",
            "data": {"status": 401},
        }
        self.adapter.wcapi = Mock(put=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("put", "products/5", data={"name": "Mask"})
        self.assertEqual(
            error.exception.args[0],
            "Error: {'code': 'woocommerce_rest_cannot_edit', 'message': 'Sorry, "
            "you are not allowed to edit this resource.', 'data': {'status': 401}} "
            "-> Op: put, Resource: products/5, Args: (), "
            "KWArgs: {'data': {'name': 'Mask'}}",
        )

    def test_connection_error_retries_the_job(self):
        self.adapter.wcapi = Mock(
            get=Mock(side_effect=requests.ConnectionError("Connection refused"))
        )
        with self.assertRaises(RetryableJobError) as error:
            self.adapter._exec("get", "products")
        self.assertEqual(
            error.exception.args[0],
            "Error connecting to WooCommerce: Connection refused",
        )

    def test_answer_that_is_not_json_shows_what_came_back(self):
        response = Mock(
            url="https://shop.example.com/wp-json/wc/v3/products",
            text=(
                "<html><body>Briefly unavailable for scheduled maintenance."
                "</body></html>"
            ),
        )
        response.json.side_effect = requests.JSONDecodeError(
            "Expecting value", response.text, 0
        )
        response.request = Mock(headers={"Accept": "application/json"}, method="POST")
        self.adapter.wcapi = Mock(post=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("post", "products", data={"name": "Mask"})
        self.assertEqual(
            error.exception.args[0],
            "Error decoding json WooCommerce response: Expecting value: line 1 "
            "column 1 (char 0)\nArgs:()\nKwargs:{'data': {'name': 'Mask'}}\n"
            "URL:https://shop.example.com/wp-json/wc/v3/products\n"
            "Headers:{'Accept': 'application/json'}\nMethod:POST\n"
            "Body:<html><body>Briefly unavailable for scheduled maintenance."
            "</body></html> ...",
        )

    def test_empty_answer_is_refused(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = None
        self.adapter.wcapi = Mock(put=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("put", "products/5", data={"name": "Mask"})
        self.assertEqual(
            error.exception.args[0], "Unexpected response from WooCommerce: None"
        )

    def test_record_answer_with_paging_headers_is_refused(self):
        response = Mock(ok=True, headers={"X-WP-Total": "1", "X-WP-TotalPages": "1"})
        response.json.return_value = {"id": 5}
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("get", "products/5")
        self.assertEqual(
            error.exception.args[0],
            "The 'X-WP-Total' header should not be present in singleton "
            "responses: {'id': 5}",
        )

    def test_list_answer_without_paging_headers_is_refused(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = [{"id": 5}]
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("get", "products")
        self.assertEqual(
            error.exception.args[0],
            "The 'X-WP-Total' header is missing in multi responses: [{'id': 5}]",
        )

    def test_list_answer_to_an_update_is_refused(self):
        response = Mock(ok=True, headers={"X-WP-Total": "1", "X-WP-TotalPages": "1"})
        response.json.return_value = [{"id": 5}]
        self.adapter.wcapi = Mock(put=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter._exec("put", "products/5", data={"name": "Mask"})
        self.assertEqual(
            error.exception.args[0],
            "Unexpected multi-response for operation 'put': [{'id': 5}]",
        )

    def test_version_of_a_shop_answering_no_status_is_refused(self):
        response = Mock(ok=True, headers={"X-WP-Total": "0", "X-WP-TotalPages": "0"})
        response.json.return_value = []
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        with self.assertRaises(ValidationError) as error:
            self.adapter.get_version()
        self.assertEqual(
            error.exception.args[0],
            "Unexpected response from WooCommerce system_status: {'data': [], "
            "'returned_items': 0, 'total_items': 0, 'total_pages': 0}",
        )
