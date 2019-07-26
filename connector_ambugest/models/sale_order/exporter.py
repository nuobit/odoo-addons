# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.addons.component.core import Component

import logging

_logger = logging.getLogger(__name__)


class SaleOrderExporter(Component):
    _name = 'ambugest.sale.order.exporter'
    _inherit = 'ambugest.exporter'
    _apply_on = 'ambugest.sale.order'

    def run(self, binding):
        external_id = self.binder.to_external(binding)
        if not external_id:
            return _('Sale is not linked with a Ambugest sales order')

        values = {
            'Odoo_Numero_Albaran': binding.name,
            'Odoo_Fecha_Generado_Albaran': fields.Date.from_string(binding.confirmation_date),
        }
        self.backend_adapter.write(external_id, values)
