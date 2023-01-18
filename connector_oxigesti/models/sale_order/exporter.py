# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrderBatchExporter(Component):
    """Export the Oxigesti Services.

    For every sale order in the list, a delayed job is created.
    """

    _name = "oxigesti.sale.order.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.sale.order"


class SaleOrderExporter(Component):
    _name = "oxigesti.sale.order.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.sale.order"

    def _create(self, values):
        raise ValidationError(
            _("It's not allowed to create a new services to Oxigesti.")
        )

    def run_invoice_data(self, binding, invoice, clear=False):
        external_id = self.binder.to_external(binding)
        if not external_id:
            return _("Sale is not linked with a Oxigesti sales order")

        invoice_number, invoice_date = None, None
        if not clear:
            invoice_number = invoice.name
            invoice_date = invoice.invoice_date

        values = {
            "Odoo_Numero_Factura": invoice_number,
            "Odoo_Fecha_Generada_Factura": invoice_date,
        }
        self.backend_adapter.write(external_id, values)
