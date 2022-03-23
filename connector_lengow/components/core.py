# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseLengowConnector(AbstractComponent):
    _name = "base.lengow.connector"
    _inherit = "base.connector"
    _collection = "lengow.backend"

    _description = "Base Lengow Connector Component"
