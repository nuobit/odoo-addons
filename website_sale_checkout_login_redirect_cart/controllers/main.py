# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.urls import url_parse

from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCheckoutLoginRedirectCart(WebsiteSale):
    def checkout_redirection(self, order):
        redirection = super().checkout_redirection(order)
        if (
            redirection
            and request.website.account_on_checkout == "mandatory"
            and request.website.is_public_user()
        ):
            location = redirection.headers.get("Location") or ""
            if url_parse(location).path == "/web/login":
                return request.redirect("/shop/cart")
        return redirection
