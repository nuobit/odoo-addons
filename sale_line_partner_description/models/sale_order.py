# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_description_values(self, product):
        values = {
            "display_name": product.display_name,
        }
        if product.description_sale:
            values["description_sale"] = product.description_sale
        return values

    def _set_description(self):
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )
        values = self._prepare_description_values(product)
        if values:
            self.name = "\n".join(values.values())

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            if not self.env.context.get("no_set_description", False):
                self._set_description()
        return res
