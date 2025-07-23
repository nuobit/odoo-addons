# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSPrescriptionTypeBatchDirectImporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.spms.prescription.type"


class OxigestiSPMSSPMSPrescriptionTypeBatchDelayedImporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.spms.prescription.type"


class OxigestiSPMSSPMSPrescriptionTypeBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.spms.prescription.type"
