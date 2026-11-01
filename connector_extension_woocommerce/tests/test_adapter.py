# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from datetime import datetime
from unittest.mock import Mock, call

from .common import WooCommerceAdapterCase


class TestAdapter(WooCommerceAdapterCase):
    def test_get_reads_every_page_at_the_backend_page_size(self):
        self.backend_record.page_size = 2
        first_page = Mock(ok=True, headers={"X-WP-Total": "3", "X-WP-TotalPages": "2"})
        first_page.json.return_value = [{"id": 1}, {"id": 2}]
        second_page = Mock(ok=True, headers={"X-WP-Total": "3", "X-WP-TotalPages": "2"})
        second_page.json.return_value = [{"id": 3}]
        self.adapter.wcapi = Mock(get=Mock(side_effect=[first_page, second_page]))
        records = self.adapter._exec("get", "products")
        self.assertEqual(records, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(
            self.adapter.wcapi.get.call_args_list,
            [
                call("products", params={"per_page": 2, "page": 1}),
                call("products", params={"per_page": 2, "page": 2}),
            ],
        )

    def test_get_returns_once_a_record_repeated_across_pages(self):
        self.backend_record.page_size = 2
        first_page = Mock(ok=True, headers={"X-WP-Total": "4", "X-WP-TotalPages": "2"})
        first_page.json.return_value = [{"id": 1}, {"id": 2}]
        second_page = Mock(ok=True, headers={"X-WP-Total": "4", "X-WP-TotalPages": "2"})
        second_page.json.return_value = [{"id": 2}, {"id": 3}]
        self.adapter.wcapi = Mock(get=Mock(side_effect=[first_page, second_page]))
        records = self.adapter._exec("get", "products")
        self.assertEqual(records, [{"id": 1}, {"id": 2}, {"id": 3}])

    def test_get_sends_modified_after_and_applies_the_other_clauses_itself(self):
        self.backend_record.page_size = 50
        response = Mock(ok=True, headers={"X-WP-Total": "2", "X-WP-TotalPages": "1"})
        response.json.return_value = [
            {"id": 1, "status": "publish"},
            {"id": 2, "status": "draft"},
        ]
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        records = self.adapter._exec(
            "get",
            "products",
            domain=[
                ("modified_after", ">=", datetime(2026, 1, 1)),
                ("status", "=", "publish"),
            ],
        )
        self.assertEqual(records, [{"id": 1, "status": "publish"}])
        self.adapter.wcapi.get.assert_called_once_with(
            "products",
            params={
                "modified_after": "2026-01-01T00:00:00Z",
                "per_page": 50,
                "page": 1,
            },
        )

    def test_get_finds_a_value_written_with_surrounding_spaces(self):
        response = Mock(ok=True, headers={"X-WP-Total": "2", "X-WP-TotalPages": "1"})
        response.json.return_value = [
            {"id": 1, "sku": "MASK-1"},
            {"id": 2, "sku": "MASK-2"},
        ]
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        records = self.adapter._exec(
            "get", "products", domain=[("sku", "=", " MASK-1 ")]
        )
        self.assertEqual(records, [{"id": 1, "sku": "MASK-1"}])

    def test_get_with_offset_and_limit_reads_only_the_pages_it_needs(self):
        self.backend_record.page_size = 2
        first_page = Mock(ok=True, headers={"X-WP-Total": "5", "X-WP-TotalPages": "3"})
        first_page.json.return_value = [{"id": 1}, {"id": 2}]
        second_page = Mock(ok=True, headers={"X-WP-Total": "5", "X-WP-TotalPages": "3"})
        second_page.json.return_value = [{"id": 3}, {"id": 4}]
        third_page = Mock(ok=True, headers={"X-WP-Total": "5", "X-WP-TotalPages": "3"})
        third_page.json.return_value = [{"id": 5}]
        self.adapter.wcapi = Mock(
            get=Mock(side_effect=[first_page, second_page, third_page])
        )
        records = self.adapter._exec("get", "products", offset=3, limit=1)
        self.assertEqual(records, [{"id": 4}])
        self.assertEqual(self.adapter.wcapi.get.call_count, 2)

    def test_get_of_one_record_returns_it_in_a_list(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = {"id": 5, "name": "Mask"}
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        records = self.adapter._exec("get", "products/5")
        self.assertEqual(records, [{"id": 5, "name": "Mask"}])

    def test_get_of_a_product_deleted_in_woocommerce_returns_nothing(self):
        response = Mock(ok=False, status_code=404)
        response.json.return_value = {
            "code": "woocommerce_rest_product_invalid_id",
            "message": "Invalid ID.",
            "data": {"status": 404},
        }
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        records = self.adapter._exec("get", "products/5")
        self.assertEqual(records, [])

    def test_total_items_come_from_the_header_of_one_call(self):
        response = Mock(ok=True, headers={"X-WP-Total": "42", "X-WP-TotalPages": "42"})
        response.json.return_value = [{"id": 7}]
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        total_items = self.adapter.get_total_items(
            "products", domain=[("modified_after", ">=", datetime(2026, 1, 1))]
        )
        self.assertEqual(total_items, 42)
        self.adapter.wcapi.get.assert_called_once_with(
            "products",
            params={
                "modified_after": "2026-01-01T00:00:00Z",
                "per_page": 1,
                "_fields": "id",
                "page": 1,
            },
        )

    def test_create_returns_the_created_record(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = {"id": 10, "name": "Mask"}
        self.adapter.wcapi = Mock(post=Mock(return_value=response))
        record = self.adapter._exec("post", "products", data={"name": "Mask"})
        self.assertEqual(record, {"id": 10, "name": "Mask"})
        self.adapter.wcapi.post.assert_called_once_with(
            "products", data={"name": "Mask"}
        )

    def test_update_returns_the_updated_record(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = {"id": 10, "name": "Face mask"}
        self.adapter.wcapi = Mock(put=Mock(return_value=response))
        record = self.adapter._exec("put", "products/10", data={"name": "Face mask"})
        self.assertEqual(record, {"id": 10, "name": "Face mask"})
        self.adapter.wcapi.put.assert_called_once_with(
            "products/10", data={"name": "Face mask"}
        )

    def test_delete_returns_the_deleted_record(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = {"id": 10, "name": "Mask"}
        self.adapter.wcapi = Mock(delete=Mock(return_value=response))
        record = self.adapter._exec("delete", "products/10", params={"force": True})
        self.assertEqual(record, {"id": 10, "name": "Mask"})
        self.adapter.wcapi.delete.assert_called_once_with(
            "products/10", params={"force": True}
        )

    def test_version_is_read_from_the_system_status(self):
        response = Mock(ok=True, headers={})
        response.json.return_value = {"environment": {"version": "9.8.5"}}
        self.adapter.wcapi = Mock(get=Mock(return_value=response))
        version = self.adapter.get_version()
        self.assertEqual(version, "9.8.5")
        self.adapter.wcapi.get.assert_called_once_with("system_status")

    def test_options_is_not_supported(self):
        with self.assertRaises(NotImplementedError):
            self.adapter._exec("options", "products")
