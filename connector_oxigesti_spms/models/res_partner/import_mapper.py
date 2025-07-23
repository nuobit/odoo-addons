# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ConnectorOxigestiSpmsImporterMapper(Component):
    _name = "oxigesti.spms.res.partner.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.res.partner"
    _usage = "import.mapper"

    # direct = [
    #     ("UnidadeLocalSalude", "name"),
    #     ("Cidade", "city"),
    #     ("CodigoPostal", "zip"),
    #     ("Domicilio", "street"),
    #     ("NIF", "vat"),
    #     ("CodigoConvencao", "ref"),
    # ]

    @only_create
    @mapping
    def name(self, record):
        return {"name": record["UnidadeLocalSalude"]}

    @only_create
    @mapping
    def city(self, record):
        return {"city": record["Cidade"]}

    @only_create
    @mapping
    def zip(self, record):
        return {"zip": record["CodigoPostal"]}

    @only_create
    @mapping
    def street(self, record):
        return {"street": record["Domicilio"]}

    @only_create
    @mapping
    def vat(self, record):
        return {"vat": record["NIF"]}

    @only_create
    @mapping
    def ref(self, record):
        return {"ref": record["CodigoConvencao"]}
