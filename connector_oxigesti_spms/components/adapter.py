# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import AbstractComponent


class ConnectorOxigestiSpmsAdapter(AbstractComponent):
    _name = "oxigesti.spms.adapter"
    _inherit = ["base.backend.mssql.adapter.crud", "oxigesti.spms.connector"]
