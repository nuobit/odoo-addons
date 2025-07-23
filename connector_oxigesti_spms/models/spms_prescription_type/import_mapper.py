# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class OxigestiSPMSSPMSPrescriptionTypeImporterMapper(Component):
    _name = "oxigesti.spms.spms.prescription.type.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.spms.prescription.type"
    _usage = "import.mapper"

    @only_create
    @mapping
    def name(self, record):
        return {"name": record["Nome"]}

    @only_create
    @mapping
    def code(self, record):
        return {"code": record["Codigo"]}
