# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.osv import expression


class Product(models.Model):
    _inherit = "product.product"

    buyer_ids = fields.One2many(
        comodel_name="product.buyerinfo", inverse_name="product_id", string="Customers"
    )

    def name_get(self):
        """Override name_get to include buyer code in the product name."""

        partner_id = self.env.context.get("partner_id")
        if partner_id and "default_description_sale" in self.env.context:
            self = self.with_context(partner_id=False)

        res = super(Product, self).name_get()
        if partner_id and "default_description_sale" in self.env.context:
            domain = [("partner_id", "=", partner_id)]
            parent = self.env["res.partner"].browse(partner_id).parent_id
            if parent:
                domain = expression.OR(
                    [
                        domain,
                        [("partner_id", "=", parent.id)],
                    ]
                )
            domain = expression.AND([domain, [("product_id", "in", self.ids)]])
            buyers = self.env["product.buyerinfo"].search(domain)
            buyer_d = {}
            for buyer in buyers:
                # build name
                name_l = []
                if buyer.code:
                    bcode = buyer.code
                else:
                    bcode = buyer.product_id.default_code
                if bcode:
                    name_l.append("[%s]" % bcode)

                if buyer.name:
                    bname = buyer.name
                else:
                    bname = buyer.product_id.name
                if bname:
                    name_l.append(bname)

                if name_l:
                    buyer_d[buyer.product_id.id] = " ".join(name_l)

            for i, elem in enumerate(res):
                product_id = elem[0]
                if product_id in buyer_d:
                    res[i] = (product_id, buyer_d[product_id])

        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        partner_id = self.env.context.get("partner_id")
        if partner_id and "default_description_sale" in self.env.context:
            self = self.with_context(partner_id=False)

        res = super(Product, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
        if partner_id and "default_description_sale" in self.env.context:
            partner_domain = [("partner_id", "=", partner_id)]
            parent = self.env["res.partner"].browse(partner_id).parent_id
            if parent:
                partner_domain = expression.OR(
                    [
                        partner_domain,
                        [("partner_id", "=", parent.id)],
                    ]
                )
            domain = expression.AND([partner_domain, [("code", operator, name)]])
            res_l = list(res)
            if res_l:
                domain = expression.AND([domain, [("product_id", "not in", res_l)]])
            buyers = self.env["product.buyerinfo"].search(domain)
            if buyers:
                res = res_l + buyers.product_id.ids
        return res
