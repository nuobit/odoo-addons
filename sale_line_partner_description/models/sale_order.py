# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_buyer_product_name(self):
        product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
        buyer_id = product.buyer_ids.filtered(
            lambda x: x.partner_id.id == self.order_id.partner_id.id
        )
        if buyer_id:
            buyer = buyer_id.with_context(
                lang=self.order_id.partner_id.lang,
            )
            product_name = buyer.get_product_name()
        else:
            product_name = False
        return product_name

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            product_name = self.get_buyer_product_name()
            if product_name:
                self.name = product_name
        return res
