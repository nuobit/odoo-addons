# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSContextBatchDirectImporter(Component):
    _name = "oxigesti.spms.spms.context.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.spms.context"


class OxigestiSPMSSPMSContextBatchDelayedImporter(Component):
    _name = "oxigesti.spms.spms.context.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.spms.context"


class OxigestiSPMSSPMSContextBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.spms.context.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.spms.context"
