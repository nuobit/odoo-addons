# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from .common import BATCH_SENDING_METHODS


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_batch_id = fields.Many2one(
        comodel_name="account.invoice.batch",
        ondelete="restrict",
        string="Invoice batch",
        tracking=True,
        copy=False,
    )
    invoice_batch_sending_method = fields.Selection(
        selection=BATCH_SENDING_METHODS,
        string="Sending method",
        tracking=True,
    )
    invoice_batch_email_partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain="[('id', 'child_of', partner_id), ('email', '!=', False)]",
        ondelete="restrict",
        string="Contact",
        tracking=True,
    )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id.invoice_batch_sending_method:
            self.invoice_batch_sending_method = (
                self.partner_id.invoice_batch_sending_method
            )
        if self.partner_id.invoice_batch_email_partner_id:
            self.invoice_batch_email_partner_id = (
                self.partner_id.invoice_batch_email_partner_id
            )
        return res
