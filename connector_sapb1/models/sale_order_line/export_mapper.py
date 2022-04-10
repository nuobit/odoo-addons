# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderLineExportMapper(Component):
    _name = 'sapb1.sale.order.line.export.mapper'
    _inherit = 'sapb1.export.mapper'

    _apply_on = 'sapb1.sale.order.line'

    direct = [
        ('price_unit', 'UnitPrice'),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def product(self, record):
        return {'ItemCode': record.product_id.code}

    @mapping
    def quantity(self, record):
        return {'Quantity': record.product_uom_qty or 1}

    @mapping
    def linenum(self, record):
        return {'LineNum': record.id}

    @mapping
    def tax(self, record):
        if not record.tax_id:
            return {'VatGroup': None}
        if len(record.tax_id) > 1:
            raise ValidationError(_("In SAP B1 only one tax can be applied to a line"))
        tax_map = self.backend_record.tax_ids.filtered(lambda x: x.tax_id == record.tax_id)
        if not tax_map:
            raise ValidationError(_('No tax mapping found for tax %s') % record.tax_id.name)
        return {'VatGroup': tax_map.sapb1_tax}
