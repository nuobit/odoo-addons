# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountInvoiceBatchProcess(models.TransientModel):
    _inherit = "account.invoice.batch.process"

    invoice_batch_sending_email_attachments = fields.Boolean(
        string="E-mail (Attach documents)", default=True
    )

    def send_email(self, move_id):
        value = self.env.context.get("skip_account_mail_attachments", True)
        self = self.with_context(skip_account_mail_attachments=value)
        return super(AccountInvoiceBatchProcess, self).send_email(move_id)

    def send_email_attachments(self, move_id):
        self.with_context(skip_account_mail_attachments=False).send_email(move_id)

    def prepare_invoices(self, invoices):
        self.ensure_one()
        res = super().prepare_invoices(invoices)

        # email attachments
        if self.invoice_batch_sending_email_attachments:
            for inv in invoices.filtered(
                lambda x: x.invoice_batch_sending_method == "emailattachments"
                and not x.is_move_sent
            ):
                self.with_delay().send_email_attachments(inv.id)

        return res
