# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSLotDirectExporter(Component):
    _name = "oxigesti.spms.spms.lot.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.spms.lot"


class OxigestiSPMSSPMSLotBatchDelayedExporter(Component):
    _name = "oxigesti.spms.spms.lot.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.spms.lot"


class OxigestiSPMSSPMSLotBatchDirectExporter(Component):
    _name = "oxigesti.spms.spms.lot.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.spms.lot"
