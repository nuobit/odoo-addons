# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooCommerceWPMLBackendAdapter(Component):
    _name = "connector.woocommerce.wpml.backend.adapter"
    _inherit = "connector.woocommerce.wpml.adapter"
    _description = "WooCommerce WPML Backend Adapter"

    _apply_on = "woocommerce.wpml.backend"
