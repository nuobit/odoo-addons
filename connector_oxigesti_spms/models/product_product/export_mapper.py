# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSpmsProductProductExportMapper(Component):
    _name = "oxigesti.spms.product.product.export.mapper"
    _inherit = "oxigesti.spms.export.mapper"

    _apply_on = "oxigesti.spms.product.product"

    direct = [
        ("default_code", "Codigo"),
        ("name", "Nome"),
        ("lst_price", "PrecoUnitario"),
    ]
