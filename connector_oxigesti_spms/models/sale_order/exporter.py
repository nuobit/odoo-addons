# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderDirectExporter(Component):
    _name = "oxigesti.spms.sale.order.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.sale.order"


class OxigestiSPMSSaleOrderBatchDelayedExporter(Component):
    _name = "oxigesti.spms.sale.order.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.sale.order"


class OxigestiSPMSSaleOrderBatchDirectExporter(Component):
    _name = "oxigesti.spms.sale.order.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.sale.order"
