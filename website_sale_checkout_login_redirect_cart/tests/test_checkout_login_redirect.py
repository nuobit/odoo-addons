# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.http import root
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("-at_install", "post_install")
class TestCheckoutLoginRedirectCart(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.public_partner = cls.website.user_id.sudo().partner_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Checkout Redirect Product",
                "list_price": 100.0,
                "sale_ok": True,
                "website_published": True,
            }
        )
        cls.user_demo.partner_id.write(
            {
                "street": "215 Vine St",
                "city": "Scranton",
                "zip": "18503",
                "country_id": cls.env.ref("base.us").id,
                "state_id": cls.env.ref("base.state_us_39").id,
                "email": "demo@example.com",
            }
        )

    def _create_cart(self, partner=None):
        partner = partner or self.public_partner
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "website_id": self.website.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def _set_session_order(self, order=None, login=None, password=None):
        session = self.authenticate(login, password)
        if order:
            session["sale_order_id"] = order.id
        root.session_store.save(session)

    def _checkout(self):
        return self.url_open("/shop/checkout", allow_redirects=False)

    def _assert_redirects_to(self, response, location):
        self.assertEqual(response.status_code, 303)
        self.assertURLEqual(response.headers["Location"], location)

    def test_mandatory_public_checkout_redirects_to_cart(self):
        self.website.account_on_checkout = "mandatory"
        self._set_session_order(self._create_cart())

        response = self._checkout()

        self._assert_redirects_to(response, "/shop/cart")

    def test_mandatory_logged_in_checkout_keeps_standard_flow(self):
        self.website.account_on_checkout = "mandatory"
        cart = self._create_cart(self.user_demo.partner_id)
        self._set_session_order(cart, self.user_demo.login, self.user_demo.login)

        response = self._checkout()

        self.assertEqual(response.status_code, 200)

    def test_non_mandatory_public_checkout_keeps_address_flow(self):
        for account_on_checkout in ("optional", "disabled"):
            with self.subTest(account_on_checkout=account_on_checkout):
                self.website.account_on_checkout = account_on_checkout
                self._set_session_order(self._create_cart())

                response = self._checkout()

                self._assert_redirects_to(response, "/shop/address")

    def test_mandatory_public_checkout_without_cart_keeps_shop_redirect(self):
        self.website.account_on_checkout = "mandatory"
        self._set_session_order()

        response = self._checkout()

        self._assert_redirects_to(response, "/shop")
