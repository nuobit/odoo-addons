# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSPMSSPMSContextExportMapper(Component):
    _name = "oxigesti.spms.spms.context.export.mapper"
    _inherit = "oxigesti.spms.export.mapper"

    _apply_on = "oxigesti.spms.spms.context"

    direct = [
        ("code", "Codigo"),
        ("name", "Nome"),
    ]
