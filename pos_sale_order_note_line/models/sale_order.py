# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models, tools, api, _
from functools import partial


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _order_line_fields(self, line):
        res = super()._order_line_fields(line)

        line_data = res[2]

        line_description_l = []
        line_name = line_data.get('name')
        if line_name:
            line_description_l.append(line_name)
        else:
            product_name = self.env['product.product'].browse(line_data['product_id']).name
            if product_name:
                line_description_l.append(product_name)

        line_note = line_data.get('note')
        if line_note:
            line_description_l.append(line_note)

        if line_description_l:
            line_data['name'] = '\n'.join(line_description_l)

        return res
