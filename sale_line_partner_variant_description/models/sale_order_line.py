# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_description_values(self, product):
        values = super()._prepare_description_values(product)
        if product.variant_description_sale:
            values.pop("description_sale", None)
            values["variant_description_sale"] = product.variant_description_sale
        return values

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(
            SaleOrderLine, self.with_context(no_set_description=True)
        ).product_id_change()
        if self.product_id:
            self._set_description()
        return res
