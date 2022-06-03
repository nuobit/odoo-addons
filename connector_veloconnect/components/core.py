# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseVeloconnectConnector(AbstractComponent):
    _name = "base.veloconnect.connector"
    _inherit = "base.connector"
    _collection = "veloconnect.backend"

    _description = "Base Veloconnect Connector Component"
