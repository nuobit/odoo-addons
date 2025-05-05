# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    max_resend_delay_email = fields.Float(default=24)
    max_resend_delay_mobile = fields.Float(default=24)
    max_resend_count_mobile = fields.Integer(default=5)
    max_resend_count_email = fields.Integer(default=5)
