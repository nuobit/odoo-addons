# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if not self.product_id:
            return res

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        buyer_id = product.buyer_ids.filtered(
            lambda x: x.partner_id.id == self.order_id.partner_id.id
        )
        if buyer_id:
            buyer = buyer_id.with_context(
                lang=self.order_id.partner_id.lang,
            )

            if buyer.code:
                code = buyer.code
            else:
                code = (
                    product._context.get("display_default_code", True)
                    and getattr(product, "default_code", False)
                    or False
                )

            if buyer.name:
                name = buyer.name
            else:
                name = product.name

            name_l = []
            if code:
                name_l.append("[%s]" % code)
            if name:
                name_l.append(name)

            if name_l:
                name_l = [" ".join(name_l)]

            if product.description_sale:
                name_l.append(product.description_sale)

            if name_l:
                self.update(
                    {
                        "name": "\n".join(name_l),
                    }
                )

        return res
