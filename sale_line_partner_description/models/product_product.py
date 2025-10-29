# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    buyer_ids = fields.One2many(
        comodel_name="product.buyerinfo", inverse_name="product_id", string="Customers"
    )

    # def _name_get_buyers(self, pairs):
    #     partner_id = self.env.context.get("sale_partner_id")
    #     if partner_id:
    #         buyers = self.env["product.buyerinfo"].search_by_partner(
    #             partner_id,
    #             [
    #                 ("product_id", "in", self.ids),
    #             ],
    #         )
    #         buyer_d = {b.product_id.id: b for b in buyers}
    #         res = []
    #         for product_id, name in pairs:
    #             if product_id in buyer_d:
    #                 buyer = buyer_d[product_id]
    #                 if buyer.code:
    #                     m = re.match(r"^\[[^]]+\] (.+)$", name)
    #                     if m:
    #                         name = f"[{buyer.code}] {m.group(1)}"
    #                 if buyer.name:
    #                     name = self._smart_update_name(name, buyer.name)
    #                     # m = re.match(r"^(\[[^]]+\]) .+$", name)
    #                     # if m:
    #                     #     name = f"{m.group(1)} {buyer.name}"
    #                     # else:
    #                     #     name = buyer.name
    #             res.append((product_id, name))
    #     else:
    #         res = pairs
    #     return res
    #
    # # TODO: Move to a mixin or sale_order_line_description_base class
    # def _context_sale_partner(self):
    #     ctx = dict(partner_id=False, seller_id=False)
    #     partner_id = self.env.context.get("partner_id")
    #     if "sale_partner_id" in self.env.context:
    #         sale_partner_id = self.env.context.get("sale_partner_id")
    #         if not sale_partner_id:
    #             raise ValidationError(
    #                 _(
    #                     "sale_partner_id cannot be False, it should be either set or absent"
    #                 )
    #             )
    #         if partner_id:
    #             raise ValidationError(
    #                 _("Cannot have both partner_id and sale_partner_id in context")
    #             )
    #     else:
    #         if partner_id:
    #             ctx["sale_partner_id"] = partner_id
    #     return ctx

    # def name_get(self):
    #     """Override name_get to include buyer code in the product name."""
    #     if "default_description_sale" in self.env.context:
    #         self = self.with_context(**self._context_sale_partner())
    #     res = super(ProductProduct, self).name_get()
    #     if "default_description_sale" in self.env.context:
    #         res = self._name_get_buyers(res)
    #     return res

    def _update_name_buyer(self, name):
        partner_id = self.env.context.get("partner_id")
        if partner_id:
            buyer = self.env["product.buyerinfo"].search_by_partner(
                partner_id,
                [
                    "&",
                    ("product_id", "=", self.id),
                    "|",
                    ("code", "!=", False),
                    ("name", "!=", False),
                ],
            )
            # It'll always be a single record due to the search_by_partner method
            if buyer:
                if buyer.code:
                    m = re.match(r"^\[[^]]+\] (.+)$", name)
                    if m:
                        name = f"[{buyer.code}] {m.group(1)}"
                if buyer.name:
                    name = self._smart_update_name(name, buyer.name)
        return name

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        name = self._update_name_buyer(name)
        return name

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
