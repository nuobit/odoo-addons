# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseWordPressConnector(AbstractComponent):
    _name = "base.wordpress.connector"
    _inherit = "base.connector"
    _collection = "wordpress.backend"

    _description = "Base WordPress Connector Component"
