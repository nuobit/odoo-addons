# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class LengowBackendAdapter(Component):
    _name = "connector.lengow.backend.adapter"
    _inherit = "connector.lengow.adapter"
    _description = "Lengow Backend Adapter"

    _apply_on = "lengow.backend"
