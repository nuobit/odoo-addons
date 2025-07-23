# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderDirectExporter(Component):
    _name = "oxigesti.spms.sale.order.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.sale.order"

    def run_invoice_data(self, binding, invoice, clear=False):
        external_id = self.binder.to_external(binding)
        if not external_id:
            return _("Sale is not linked with a Oxigesti SPMS Invoice")

        invoice_number, invoice_date = None, None
        if not clear:
            invoice_number = invoice.name
            invoice_date = invoice.invoice_date

        values = {
            "Odoo_Numero_Factura": invoice_number,
            "Odoo_Fecha_Generada_Factura": invoice_date,
        }
        self.backend_adapter.write(external_id, values)


class OxigestiSPMSSaleOrderBatchDelayedExporter(Component):
    _name = "oxigesti.spms.sale.order.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.sale.order"


class OxigestiSPMSSaleOrderBatchDirectExporter(Component):
    _name = "oxigesti.spms.sale.order.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.sale.order"
