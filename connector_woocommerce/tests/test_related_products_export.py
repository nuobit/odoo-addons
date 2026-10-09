# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from .common import WooCommerceCase


class TestRelatedProductsExport(WooCommerceCase):
    """A product sends to the shop only the alternatives and the accessories
    that have the WooCommerce check: the export buttons select only the checked
    products, so nothing would ever update the others there."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template.write({"default_code": "WC-RELATED", "taxes_id": [(5, 0, 0)]})

    def _export_through_the_shop(self, template):
        """Export ``template`` and return the shop's create and update requests.

        The shop finds no product by SKU and answers each create with the next
        shop id, 4001 first."""
        requests = []

        def shop(op, resource, *args, **kwargs):
            if op == "get":
                return []
            requests.append((op, resource, kwargs["data"]))
            return {**kwargs["data"], "id": 4000 + len(requests)}

        with self.backend.work_on("woocommerce.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            # Stop only at the external API boundary; run the real exporters
            with patch.object(type(adapter), "_exec", side_effect=shop):
                self.env["woocommerce.product.template"].export_record(
                    self.backend, template
                )
        return requests

    def test_product_export_creates_only_the_alternatives_with_the_check(self):
        sold = self._create_template("Alternative sold in the shop")
        sold.write({"default_code": "WC-SOLD", "taxes_id": [(5, 0, 0)]})
        not_sold = self._create_template("Alternative not sold in the shop")
        not_sold.write(
            {
                "default_code": "WC-NOT-SOLD",
                "taxes_id": [(5, 0, 0)],
                "woocommerce_enabled": False,
            }
        )
        self.template.alternative_product_ids = sold | not_sold
        requests = self._export_through_the_shop(self.template)
        self.assertEqual(
            [(op, resource, data["sku"]) for op, resource, data in requests],
            [("post", "products", "WC-SOLD"), ("put", "products/1001", "WC-RELATED")],
        )
        self.assertEqual(sold.woocommerce_bind_ids.woocommerce_idproduct, 4001)
        self.assertFalse(not_sold.woocommerce_bind_ids)
        self.assertEqual(requests[1][2]["upsell_ids"], [4001])

    def test_product_export_creates_only_the_accessories_with_the_check(self):
        sold = self._create_template("Accessory sold in the shop")
        sold.write({"default_code": "WC-SOLD", "taxes_id": [(5, 0, 0)]})
        not_sold = self._create_template("Accessory not sold in the shop")
        not_sold.write(
            {
                "default_code": "WC-NOT-SOLD",
                "taxes_id": [(5, 0, 0)],
                "woocommerce_enabled": False,
            }
        )
        self.template.accessory_product_ids = (
            sold.product_variant_id | not_sold.product_variant_id
        )
        requests = self._export_through_the_shop(self.template)
        self.assertEqual(
            [(op, resource, data["sku"]) for op, resource, data in requests],
            [("post", "products", "WC-SOLD"), ("put", "products/1001", "WC-RELATED")],
        )
        self.assertEqual(sold.woocommerce_bind_ids.woocommerce_idproduct, 4001)
        self.assertFalse(not_sold.woocommerce_bind_ids)
        self.assertEqual(requests[1][2]["cross_sell_ids"], [4001])

    def test_upsells_list_only_the_alternatives_with_the_check(self):
        sold = self._create_template("Alternative sold in the shop", 2001)
        # Already in the shop: sent before the check was required
        not_sold = self._create_template("Alternative not sold in the shop", 2002)
        not_sold.woocommerce_enabled = False
        self.template.alternative_product_ids = sold | not_sold
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["upsell_ids"], [2001])

    def test_upsells_are_emptied_when_no_alternative_has_the_check(self):
        # Already in the shop: sent before the check was required
        not_sold = self._create_template("Alternative not sold in the shop", 2002)
        not_sold.woocommerce_enabled = False
        self.template.alternative_product_ids = not_sold
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["upsell_ids"], [])

    def test_upsells_list_archived_alternatives_only_without_active_test(self):
        sold = self._create_template("Alternative sold in the shop", 2001)
        archived = self._create_template("Archived alternative sold in the shop", 2005)
        archived.active = False
        self.template.alternative_product_ids = sold | archived
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["upsell_ids"], [2001])
        # The export batches read without active_test
        payload = self._export_payload(
            "woocommerce.product.template",
            self.template.with_context(active_test=False),
            [1001],
        )
        self.assertEqual(payload["upsell_ids"], [2001, 2005])

    def test_cross_sells_list_only_the_accessories_with_the_check(self):
        sold = self._create_template("Accessory sold in the shop", 2003)
        # Already in the shop: sent before the check was required
        not_sold = self._create_template("Accessory not sold in the shop", 2004)
        not_sold.woocommerce_enabled = False
        self.template.accessory_product_ids = (
            sold.product_variant_id | not_sold.product_variant_id
        )
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["cross_sell_ids"], [2003])

    def test_cross_sells_are_emptied_when_no_accessory_has_the_check(self):
        # Already in the shop: sent before the check was required
        not_sold = self._create_template("Accessory not sold in the shop", 2004)
        not_sold.woocommerce_enabled = False
        self.template.accessory_product_ids = not_sold.product_variant_id
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["cross_sell_ids"], [])

    def test_cross_sells_list_archived_accessories_only_without_active_test(self):
        sold = self._create_template("Accessory sold in the shop", 2003)
        archived = self._create_template("Archived accessory sold in the shop", 2006)
        self.template.accessory_product_ids = (
            sold.product_variant_id | archived.product_variant_id
        )
        archived.active = False
        payload = self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )
        self.assertEqual(payload["cross_sell_ids"], [2003])
        # The export batches read without active_test
        payload = self._export_payload(
            "woocommerce.product.template",
            self.template.with_context(active_test=False),
            [1001],
        )
        self.assertEqual(payload["cross_sell_ids"], [2003, 2006])
