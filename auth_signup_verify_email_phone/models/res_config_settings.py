# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    max_resend_delay_email = fields.Float(
        related="company_id.max_resend_delay_email",
        readonly=False,
    )
    max_resend_delay_mobile = fields.Float(
        related="company_id.max_resend_delay_mobile",
        readonly=False,
    )
    max_resend_count_email = fields.Integer(
        related="company_id.max_resend_count_email",
        readonly=False,
    )
    max_resend_count_mobile = fields.Integer(
        related="company_id.max_resend_count_mobile",
        readonly=False,
    )
