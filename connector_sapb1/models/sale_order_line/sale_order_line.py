# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sapb1_bind_ids = fields.One2many(
        comodel_name='sapb1.sale.order.line',
        inverse_name='odoo_id',
        string='SAP B1 Bindings',
    )

    @api.multi
    def get_raw_price_unit(self):
        self.ensure_one()
        price_unit = self.price_unit
        if self.tax_id:
            if len(self.tax_id) > 1:
                raise ValidationError(_('Only one tax supported per order line'))
            if self.tax_id.amount_type != 'percent':
                raise ValidationError(_('Only percentage taxes supported'))
            if self.tax_id.price_include:
                price_unit /= 1 + self.tax_id.amount / 100
        return price_unit
