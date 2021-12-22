# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_invoice_batch_sending_email_template_id = fields.Many2one(
        string="Default Invoice batches e-mail template",
        comodel_name="mail.template",
        domain=[("model_id", "=", "account.invoice")],
    )
