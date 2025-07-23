# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSSuspensionReasonDirectExporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.spms.suspension.reason"


class OxigestiSPMSSPMSSuspensionReasonBatchDelayedExporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.spms.suspension.reason"


class OxigestiSPMSSPMSSuspensionReasonBatchDirectExporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.spms.suspension.reason"
