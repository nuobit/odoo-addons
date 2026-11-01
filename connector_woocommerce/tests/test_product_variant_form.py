# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import TransactionCase


class TestProductVariantForm(TransactionCase):
    """The variant form hides the shop flags, is_published and
    woocommerce_enabled, from the connector managers only, as on 14.0."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant_form_view = cls.env.ref("product.product_normal_form_view")
        cls.connector_manager = cls.env["res.users"].create(
            {
                "name": "Connector Manager",
                "login": "wc_variant_form_connector_manager",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("connector.group_connector_manager").id,
                        ],
                    )
                ],
            }
        )
        cls.employee = cls.env["res.users"].create(
            {
                "name": "Employee",
                "login": "wc_variant_form_employee",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )

    def test_connector_manager_gets_neither_shop_flag(self):
        arch = (
            self.env["product.product"]
            .with_user(self.connector_manager)
            .get_view(self.variant_form_view.id, "form")["arch"]
        )
        form = etree.fromstring(arch)
        self.assertFalse(
            form.xpath("//group[@name='extra_info']/field[@name='is_published']")
        )
        self.assertFalse(form.xpath("//field[@name='woocommerce_enabled']"))

    def test_other_users_get_the_shop_flags(self):
        arch = (
            self.env["product.product"]
            .with_user(self.employee)
            .get_view(self.variant_form_view.id, "form")["arch"]
        )
        form = etree.fromstring(arch)
        [woocommerce_enabled] = form.xpath("//field[@name='woocommerce_enabled']")
        self.assertIsNone(woocommerce_enabled.get("invisible"))
        # website_sale_variant hides is_published from every user and shows
        # its own «Published» in its place, as on 14.0
        [is_published] = form.xpath(
            "//group[@name='extra_info']/field[@name='is_published']"
        )
        self.assertEqual(is_published.get("invisible"), "1")
