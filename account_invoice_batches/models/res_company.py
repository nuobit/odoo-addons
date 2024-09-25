# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_batch_sending_email_template_id = fields.Many2one(
        string="Default Invoice batches e-mail template",
        comodel_name="mail.template",
        domain=[("model_id", "=", "account.move")],
    )
    report_intermediary_service_id = fields.Many2one(
        string="Default Report for Intermediary Service Partner",
        comodel_name="ir.actions.report",
        domain=[("model", "=", "account.move")],
    )
