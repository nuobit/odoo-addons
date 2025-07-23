# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSSuspensionReasonBatchDirectImporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.spms.suspension.reason"


class OxigestiSPMSSPMSSuspensionReasonBatchDelayedImporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.spms.suspension.reason"


class OxigestiSPMSSPMSSuspensionReasonBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.spms.suspension.reason.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.spms.suspension.reason"
