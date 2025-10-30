# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    buyer_ids = fields.One2many(
        comodel_name="product.buyerinfo", inverse_name="product_id", string="Customers"
    )

    def _clear_context_suppliers(self):
        """
        Clear context keys that would make name_get use suppliers
        instead of sale order partner.
        :return: self with updated context
        """
        # We cannot use self.env.context.get('partner') here because is
        # product_id_change who sets the 'partner' in context and not
        # always this method is executed triggered by that onchange.
        if "default_description_sale" in self.env.context:
            ctx = dict(partner_id=False, seller_id=False)
            partner = self.env.context.get("partner")
            if not partner:
                partner_id = self.env.context.get("partner_id")
                if partner_id:
                    partner = self.env["res.partner"].browse(partner_id)
                    ctx["partner"] = partner
            self = self.with_context(**ctx)
        return self

    def _get_buyer_data(self):
        buyer_d = {}
        partner = self.env.context.get("partner")
        if partner:
            buyers = self.env["product.buyerinfo"].search_by_partner(
                partner.id,
                [
                    ("product_id", "in", self.ids),
                ],
            )
            buyer_d = {b.product_id.id: b for b in buyers}
        return buyer_d

    def _name_get_buyers(self, pairs):
        buyer_d = self._get_buyer_data()
        if buyer_d:
            res = []
            for product_id, name in pairs:
                if product_id in buyer_d:
                    buyer = buyer_d[product_id]
                    if buyer.code:
                        m = re.match(r"^\[[^]]+\] (.+)$", name)
                        if m:
                            name = f"[{buyer.code}] {m.group(1)}"
                    if buyer.name:
                        m = re.match(r"^(\[[^]]+\]) .+$", name)
                        if m:
                            name = f"{m.group(1)} {buyer.name}"
                        else:
                            name = buyer.name
                res.append((product_id, name))
        else:
            res = pairs
        return res

    def name_get(self):
        """Override name_get to include buyer code in the product name."""
        self = self._clear_context_suppliers()
        res = super(ProductProduct, self).name_get()
        if "default_description_sale" in self.env.context:
            res = self._name_get_buyers(res)
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        partner_id = self.env.context.get("partner_id")
        res = super(ProductProduct, self.with_context(partner_id=False))._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
        if "default_description_sale" in self.env.context:
            if partner_id:
                domain = [
                    ("code", operator, name),
                ]
                res_l = list(res)
                if res_l:
                    domain = expression.AND([domain, [("product_id", "not in", res_l)]])
                buyers = self.env["product.buyerinfo"].search_by_partner(
                    partner_id, domain
                )
                if buyers:
                    res = res_l + buyers.product_id.ids
        return res
