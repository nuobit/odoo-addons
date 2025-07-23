# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSPMSExportMapper(AbstractComponent):
    _name = "oxigesti.spms.export.mapper"
    _inherit = ["connector.extension.export.mapper", "oxigesti.spms.connector"]
