# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class SaleOrderLineBatchImporter(Component):
    """ Import the Oxigesti Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'oxigesti.sale.order.line.delayed.batch.importer'
    _inherit = 'oxigesti.delayed.batch.importer'

    _apply_on = 'oxigesti.sale.order.line'


class SaleOrderLineImporter(Component):
    _name = 'oxigesti.sale.order.line.importer'
    _inherit = 'oxigesti.importer'
    
    _apply_on = 'oxigesti.sale.order.line'

    def _import_dependencies(self):
        ### product
        exporter = self.component(usage='direct.batch.exporter',
                                  model_name='oxigesti.product.product')
        exporter.run(domain=[
            ('company_id', '=', self.backend_record.company_id.id),
            ('default_code', '=', str(self.external_data['Articulo'])),
        ])
