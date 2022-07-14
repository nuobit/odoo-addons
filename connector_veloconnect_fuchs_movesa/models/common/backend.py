# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class VeloconnectBackend(models.Model):
    _inherit = "veloconnect.backend"

    is_fuchs_movesa = fields.Boolean(string="Is Fuchs Movesa", default=False)
