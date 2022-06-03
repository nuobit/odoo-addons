# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class ProductSupplierinfoImportMapper(Component):
    _name = 'veloconnect.product.supplierinfo.import.mapper'
    _inherit = 'veloconnect.import.mapper'

    _apply_on = 'veloconnect.product.supplierinfo'

    # @only_create
    # @mapping
    # def backend_id(self, record):
    #     return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def partner(self, record):
        return {'name': self.backend_record.partner_id.id}

    @mapping
    def currency(self, record):
        return {'currency_id': self.env['res.currency'].search([('name', '=', record['amountCurrencyID'])]).id}

    @mapping
    def product_code(self, record):
        return {'product_code': record['SellersItemIdentificationID']}

    @mapping
    def min_quantity(self, record):
        return {'min_qty': record['MinimumQuantity'] or 0}

    @mapping
    def price(self, record):
        return {'price': record['PriceAmount']}
