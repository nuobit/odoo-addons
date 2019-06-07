# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
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
            uom=self.product_uom.id
        )

        description_l = [product.name_get()[0][1]]

        buyer_id = product.buyer_ids. \
            filtered(lambda x: x.partner_id.id == self.order_id.partner_id.id)
        if buyer_id:
            buyer = buyer_id.with_context(
                lang=self.order_id.partner_id.lang,
            )
            if not buyer.concatenate:
                description_l = [buyer.name]
            else:
                description_l.append(buyer.name)
        else:
            if product.description_sale:
                description_l.append(product.description_sale)

        self.update({
            'name': '\n'.join(description_l),
        })

        return res
