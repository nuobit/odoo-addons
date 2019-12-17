# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create, convert)


class SaleOrderLineImportMapper(Component):
    _name = 'oxigesti.sale.order.line.import.mapper'
    _inherit = 'oxigesti.import.mapper'

    _apply_on = 'oxigesti.sale.order.line'

    direct = [
        (convert('Cantidad', float), 'product_uom_qty'),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def product(self, record):
        oxigesti_articulo = str(record['Articulo'])
        binding = self.env['oxigesti.product.product'].search([
            ('company_id', '=', self.backend_record.company_id.id),
            ('default_code', '=', oxigesti_articulo),
        ])
        if not binding:
            raise AssertionError("Product %s should have been exported in "
                                 "SaleOrderLineExporter._sync_dependencies" % (oxigesti_articulo,))
        if len(binding) > 1:
            raise AssertionError("Found more than 1 products (%i) with "
                                 "the same code (%s) in Odoo: %s" % (
                                     len(binding), oxigesti_articulo,
                                     binding.mapped('odoo_id.id')))

        return {'product_id': binding.odoo_id.id}
