# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooCommerceBackendAdapter(Component):
    _name = "connector.woocommerce.backend.adapter"
    _inherit = "connector.woocommerce.adapter"
    _description = "WooCommerce Backend Adapter"

    _apply_on = "woocommerce.backend"
