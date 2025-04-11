# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    buyer_ids = fields.One2many(
        comodel_name="product.buyerinfo", inverse_name="product_id", string="Customers"
    )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        products_name = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if name:
            # The 'default_description_sale' context is only used in sale.order and
            # sale.order.line views from the 'sale' module. It's better to use this
            # native context instead of extending the view context, avoiding conflicts
            # with other modules.
            if "default_description_sale" in self.env.context:
                buyers = self.env["product.buyerinfo"].search(
                    [("code", operator, name)]
                )
                for bi in buyers:
                    _id, display_name = bi.product_id.name_get()[0]
                    products_name.append((_id, "[{}] {}".format(bi.code, display_name)))
        return products_name
