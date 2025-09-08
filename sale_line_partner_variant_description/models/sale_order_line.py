# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            buyer_product_name = self.get_buyer_product_name()
            if buyer_product_name:
                if buyer_product_name != self.name:
                    self.name = buyer_product_name
        return res
