# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class AnphitrionBackendAdapter(Component):
    _name = "anphitrion.backend.adapter"
    _inherit = "anphitrion.adapter"
    _description = "Anphitrion Backend Adapter"

    _apply_on = "anphitrion.backend"
