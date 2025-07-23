# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSContextDirectExporter(Component):
    _name = "oxigesti.spms.spms.context.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.spms.context"


class OxigestiSPMSSPMSContextBatchDelayedExporter(Component):
    _name = "oxigesti.spms.spms.context.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.spms.context"


class OxigestiSPMSSPMSContextBatchDirectExporter(Component):
    _name = "oxigesti.spms.spms.context.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.spms.context"
