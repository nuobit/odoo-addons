# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase


class WooCommerceCase(SavepointComponentCase):
    """Backend, discount pricelist and bound products without any HTTP call."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._write_dates = {}
        lang = cls.env.ref("base.lang_en")
        cls.discount_pricelist = cls.env["product.pricelist"].create(
            {"name": "WooCommerce discount pricelist"}
        )
        cls.other_pricelist = cls.env["product.pricelist"].create(
            {"name": "Other pricelist"}
        )
        cls.backend = cls.env["woocommerce.backend"].create(
            {
                "name": "WooCommerce test backend",
                "url": "http://127.0.0.1:1",
                "consumer_key": "ck_test",
                "consumer_secret": "cs_test",
                "lang_ids": [(6, 0, lang.ids)],
                "language_id": lang.id,
                "client_order_ref_prefix": "WC",
                "stock_location_ids": [
                    (6, 0, cls.env.ref("stock.stock_location_stock").ids)
                ],
                "discount_pricelist_id": cls.discount_pricelist.id,
            }
        )
        cls.category = cls.env["product.category"].create(
            {"name": "WooCommerce test category"}
        )
        cls.template = cls._create_template("WooCommerce bound product", 1001)
        cls.unbound_template = cls._create_template("WooCommerce unbound product")

    @classmethod
    def _create_template(cls, name, woocommerce_idproduct=None, list_price=100.0):
        template = cls.env["product.template"].create(
            {
                "name": name,
                "list_price": list_price,
                "categ_id": cls.category.id,
                "woocommerce_enabled": True,
            }
        )
        if woocommerce_idproduct:
            cls.env["woocommerce.product.template"].create(
                {
                    "odoo_id": template.id,
                    "backend_id": cls.backend.id,
                    "woocommerce_idproduct": woocommerce_idproduct,
                }
            )
        cls._remember_write_dates(template)
        return template

    @classmethod
    def _bind_variant(cls, variant, woocommerce_idproduct):
        return cls.env["woocommerce.product.product"].create(
            {
                "odoo_id": variant.id,
                "backend_id": cls.backend.id,
                "woocommerce_idproduct": woocommerce_idproduct,
                "woocommerce_idparent": woocommerce_idproduct + 1,
            }
        )

    @classmethod
    def _remember_write_dates(cls, template):
        variants = template.with_context(active_test=False).product_variant_ids
        for records in (template, variants):
            for record in records:
                cls._write_dates[
                    record._name, record.id
                ] = record.woocommerce_write_date

    def _create_rule(self, pricelist=None, **values):
        vals = {
            "pricelist_id": (pricelist or self.discount_pricelist).id,
            "applied_on": "1_product",
            "product_tmpl_id": self.template.id,
            "compute_price": "fixed",
            "fixed_price": 80.0,
        }
        vals.update(values)
        return self.env["product.pricelist.item"].create(vals)

    def assert_touched(self, records):
        for record in records:
            self.assertNotEqual(
                record.woocommerce_write_date,
                self._write_dates[record._name, record.id],
                "%s should have been marked for export" % record.display_name,
            )

    def assert_untouched(self, records):
        for record in records:
            self.assertEqual(
                record.woocommerce_write_date,
                self._write_dates[record._name, record.id],
                "%s should not have been marked for export" % record.display_name,
            )
