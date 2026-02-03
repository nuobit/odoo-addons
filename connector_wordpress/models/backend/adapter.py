# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WordPressBackendAdapter(Component):
    _name = "wordpress.backend.adapter"
    _inherit = "wordpress.adapter"
    _description = "WordPress Backend Adapter"

    _apply_on = "wordpress.backend"
