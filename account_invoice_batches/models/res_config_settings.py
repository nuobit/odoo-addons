# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_batch_sending_email_template_id = fields.Many2one(
        related="company_id.invoice_batch_sending_email_template_id",
        readonly=False,
    )
    report_intermediary_service_id = fields.Many2one(
        related="company_id.report_intermediary_service_id",
        readonly=False,
    )
