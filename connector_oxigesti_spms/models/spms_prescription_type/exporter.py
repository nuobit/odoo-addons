# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSPMSPrescriptionTypeDirectExporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.spms.prescription.type"


class OxigestiSPMSSPMSPrescriptionTypeBatchDelayedExporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.spms.prescription.type"


class OxigestiSPMSSPMSPrescriptionTypeBatchDirectExporter(Component):
    _name = "oxigesti.spms.spms.prescription.type.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.spms.prescription.type"
