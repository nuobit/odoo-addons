# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseWooCommerceConnector(AbstractComponent):
    _name = "base.woocommerce.connector"
    _inherit = "base.connector"
    _collection = "woocommerce.backend"

    _description = "Base WooCommerce Connector Component"
