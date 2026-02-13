# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBit Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    buyer_ids = fields.One2many(
        comodel_name="product.buyerinfo", inverse_name="product_id", string="Customers"
    )

    def _get_buyer_for_partner(self, partner_id):
        self.ensure_one()
        if not partner_id:
            return self.env["product.buyerinfo"]

        buyers = self.env["product.buyerinfo"].search_by_partner(
            partner_id,
            [("product_id", "=", self.id)],
        )
        return buyers

    def get_product_multiline_description_sale(self):
        partner_id = self.env.context.get("partner_id")
        # partner = self.env["res.partner"].browse(partner_id) if partner_id else None
        if not partner_id:
            sale_line_id = self.env.context.get("sale_line_id")
            if sale_line_id:
                sale_line = self.env["sale.order.line"].browse(sale_line_id)
                partner_id = sale_line.order_partner_id

        buyer = self._get_buyer_for_partner(partner_id)

        if buyer and (buyer.code or buyer.name):
            name = self.display_name

            if buyer.code:
                m = re.match(r"^\[[^]]+\] (.+)$", name, re.DOTALL)
                if m:
                    name = f"[{buyer.code}] {m.group(1)}"
                else:
                    name = f"[{buyer.code}] {name}"

            if buyer.name:
                m = re.match(r"^(\[[^]]+\]) .+$", name, re.DOTALL)
                if m:
                    name = f"{m.group(1)} {buyer.name}"
                else:
                    name = buyer.name
            if self.description_sale:
                name += "\n" + self.description_sale

            return name
        return super().get_product_multiline_description_sale()

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)

        partner_id = self.env.context.get("partner_id")
        if not partner_id:
            sale_line_id = self.env.context.get("sale_line_id")
            if sale_line_id:
                sale_line = self.env["sale.order.line"].browse(sale_line_id)
                partner_id = sale_line.order_partner_id.id

        if not partner_id or not value:
            return domain

        buyer_domain = [
            ("partner_id", "=", partner_id),
            "|",
            ("code", operator, value),
            ("name", operator, value),
        ]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return expression.AND(
                [
                    domain,
                    [
                        (
                            "id",
                            "not in",
                            self.env["product.buyerinfo"]
                            ._search(buyer_domain)
                            .subselect("product_id"),
                        )
                    ],
                ]
            )
        return expression.OR(
            [
                domain,
                [
                    (
                        "id",
                        "in",
                        self.env["product.buyerinfo"]
                        ._search(buyer_domain)
                        .subselect("product_id"),
                    )
                ],
            ]
        )
