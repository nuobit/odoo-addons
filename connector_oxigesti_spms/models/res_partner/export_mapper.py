# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSpmsResPartnerExportMapper(Component):
    _name = "oxigesti.spms.res.partner.export.mapper"
    _inherit = "oxigesti.spms.export.mapper"

    _apply_on = "oxigesti.spms.res.partner"

    direct = [
        ("name", "UnidadeLocalSalude"),
        ("city", "Cidade"),
        ("zip", "CodigoPostal"),
        ("street", "Domicilio"),
        ("vat", "NIF"),
        ("ref", "CodigoConvencao"),
    ]
