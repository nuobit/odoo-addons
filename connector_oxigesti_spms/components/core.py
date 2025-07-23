# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSPMSConnector(AbstractComponent):
    _name = "oxigesti.spms.connector"
    _inherit = "base.connector"
    _collection = "oxigesti.spms.backend"

    _description = "Oxigesti SPMS Core Connector Component"
