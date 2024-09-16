# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseWooCommerceWPMLConnector(AbstractComponent):
    _name = "base.woocommerce.wpml.connector"
    _inherit = "base.connector"
    _collection = "woocommerce.wpml.backend"

    _description = "Base WooCommerce WPML Connector Component"
