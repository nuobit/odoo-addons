# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSLotBatchDirectImporter(Component):
    _name = "oxigesti.spms.spms.lot.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.spms.lot"


class OxigestiSPMSSPMSLotBatchDelayedImporter(Component):
    _name = "oxigesti.spms.spms.lot.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.spms.lot"


class OxigestiSPMSSPMSLotBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.spms.lot.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.spms.lot"
