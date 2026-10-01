# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceCase


class TestExportMapperCategories(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template.write({"default_code": "WC-CATEGORIES", "taxes_id": [(5, 0, 0)]})
        cls.public_category_1 = cls.env["product.public.category"].create(
            {"name": "First website category", "slug_name": "first-website-category"}
        )
        cls.public_category_2 = cls.env["product.public.category"].create(
            {"name": "Second website category", "slug_name": "second-website-category"}
        )

    def _template_payload(self):
        return self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )

    def test_template_without_categories_sends_empty_list(self):
        self.template.write({"public_categ_ids": [(5, 0, 0)]})
        self.assertEqual(self._template_payload()["categories"], [])

    def test_template_category_is_exported(self):
        self.env["woocommerce.product.public.category"].create(
            {
                "odoo_id": self.public_category_1.id,
                "backend_id": self.backend.id,
                "woocommerce_idpubliccategory": 2001,
            }
        )
        self.template.public_categ_ids = self.public_category_1
        self.assertEqual(self._template_payload()["categories"], [{"id": 2001}])

    def test_template_multiple_categories_are_exported(self):
        self.env["woocommerce.product.public.category"].create(
            {
                "odoo_id": self.public_category_1.id,
                "backend_id": self.backend.id,
                "woocommerce_idpubliccategory": 2001,
            }
        )
        self.env["woocommerce.product.public.category"].create(
            {
                "odoo_id": self.public_category_2.id,
                "backend_id": self.backend.id,
                "woocommerce_idpubliccategory": 2002,
            }
        )
        self.template.write(
            {
                "public_categ_ids": [
                    (6, 0, [self.public_category_1.id, self.public_category_2.id])
                ]
            }
        )
        self.assertCountEqual(
            self._template_payload()["categories"], [{"id": 2001}, {"id": 2002}]
        )

    def test_template_removing_last_category_sends_empty_list(self):
        self.env["woocommerce.product.public.category"].create(
            {
                "odoo_id": self.public_category_1.id,
                "backend_id": self.backend.id,
                "woocommerce_idpubliccategory": 2001,
            }
        )
        self.template.public_categ_ids = self.public_category_1
        self.assertEqual(self._template_payload()["categories"], [{"id": 2001}])

        self.template.write({"public_categ_ids": [(5, 0, 0)]})

        self.assertEqual(self._template_payload()["categories"], [])
