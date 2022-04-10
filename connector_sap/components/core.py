# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseSapConnector(AbstractComponent):
    _name = "base.sap.connector"
    _inherit = "base.connector"
    _collection = "sap.backend"

    _description = "Base Sap Connector Component"
