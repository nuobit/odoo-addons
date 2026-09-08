# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoiceBatchProcess(models.TransientModel):
    _name = "account.invoice.batch.process"
    _description = "Account Invoice Batch Process"

    @property
    def company_id(self):
        context = self.env.context or {}
        model = context.get("active_model")
        active_ids = context.get("active_ids")

        active_objects = self.env[model].browse(active_ids)
        company = active_objects.mapped("company_id")

        if model not in ("account.invoice.batch", "account.move"):
            raise UserError(_("Unexpected model '%s'" % model))

        if len(company) > 1:
            raise UserError(
                _(
                    "More than one company found. The data selected must be of the same company"
                )
            )

        return company

    invoice_batch_sending_pdf = fields.Boolean(string="PDF", default=True)
    invoice_batch_sending_email = fields.Boolean(string="E-mail", default=True)
    invoice_batch_sending_email_template_id = fields.Many2one(
        string="E-mail template",
        comodel_name="mail.template",
        domain=[("model_id", "=", "account.move")],
        default=lambda self: self.company_id.invoice_batch_sending_email_template_id,
    )
    invoice_batch_sending_signedfacturae = fields.Boolean(
        string="Factura-e signed", default=True
    )
    invoice_batch_sending_unsignedfacturae = fields.Boolean(
        string="Factura-e unsigned", default=True
    )

    def send_facturae(self, move_id):
        inv = self.env["account.move"].browse(move_id)
        if not inv.is_move_sent:
            self = self.with_context(lang=inv.partner_id.lang)
            if inv.invoice_batch_sending_method == "signedfacturae":
                move_file = self.env.ref(
                    "l10n_es_facturae.report_facturae_signed"
                )._render(inv.ids)[0]
                file_name = (_("facturae") + "_" + inv.name + ".xsig").replace("/", "-")
            else:
                move_file = self.env.ref("l10n_es_facturae.report_facturae")._render(
                    inv.ids
                )[0]
                file_name = (_("facturae") + "_" + inv.name + ".xml").replace("/", "-")

            file = base64.b64encode(move_file)
            self.env["ir.attachment"].create(
                {
                    "name": file_name,
                    "datas": file,
                    "res_model": "account.move",
                    "res_id": inv.id,
                    "mimetype": "application/xml",
                }
            )
            inv.is_move_sent = True

    def send_email(self, move_id):
        inv = self.env["account.move"].browse(move_id)
        if not inv.is_move_sent:
            template_id = self.invoice_batch_sending_email_template_id.id
            batch = inv.invoice_batch_id
            if batch:
                # the e-mail belongs to the invoice batch user of the batch
                # company: author of the message, mailbox of the replies. Only
                # that company stays among the allowed ones, and a configuration
                # withdrawn between the enqueue and the run fails loud here
                # instead of running with another identity.
                user = batch.company_id._get_invoice_batch_user()
                inv = inv.with_user(user).with_context(
                    allowed_company_ids=batch.company_id.ids
                )
            # an invoice outside a batch keeps the launcher's identity
            inv.with_context(lang=inv.partner_id.lang).message_post_with_template(
                template_id,
                message_type="comment",
                composition_mode="mass_mail",
            )
            inv.is_move_sent = True

    def _invoice_batch_user_required(self):
        """Whether the processing needs the invoice batch user of the companies.

        Only the e-mail job runs as that user: printing and factura-e keep the
        launcher's identity, so a batch of a company without user can still be
        printed or sent as factura-e.
        """
        self.ensure_one()
        return bool(self.invoice_batch_sending_email)

    def _invoice_batch_check_users(self, batches):
        """Fail before enqueueing anything when a batch company has no valid user."""
        for company in batches.mapped("company_id"):
            company._get_invoice_batch_user()

    def prepare_invoices(self, invoices):
        self.ensure_one()

        # facturae
        sending_facturae = list(
            filter(
                None,
                [
                    self.invoice_batch_sending_signedfacturae
                    and "signedfacturae"
                    or None,
                    self.invoice_batch_sending_unsignedfacturae
                    and "unsignedfacturae"
                    or None,
                ],
            )
        )
        if sending_facturae:
            for inv in invoices.filtered(
                lambda x: x.invoice_batch_sending_method in sending_facturae
                and not x.is_move_sent
            ):
                self.with_delay().send_facturae(inv.id)

        # email
        if self.invoice_batch_sending_email:
            for inv in invoices.filtered(
                lambda x: x.invoice_batch_sending_method == "email"
                and not x.is_move_sent
            ):
                self.with_delay().send_email(inv.id)

        # pdf
        if self.invoice_batch_sending_pdf:
            return invoices.filtered(lambda x: x.invoice_batch_sending_method == "pdf")

        return self.env["account.move"]

    def process_invoices(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        model = context.get("active_model")

        active_objects = self.env[model].browse(context.get("active_ids"))
        invoices_pdf = self.env["account.move"]
        if model == "account.invoice.batch":
            if not active_objects.mapped("unsent_invoice_ids"):
                raise UserError(_("There's no invoices to process"))
            if self._invoice_batch_user_required():
                self._invoice_batch_check_users(active_objects)
            for batch in active_objects:
                invoices = batch.unsent_invoice_ids
                invoices_pdf += self.prepare_invoices(invoices)
        elif model == "account.move":
            if not active_objects:
                raise UserError(_("There's no invoices to process"))
            invoices = active_objects.filtered(
                lambda x: x.invoice_batch_id and not x.is_move_sent
            )
            if self._invoice_batch_user_required():
                self._invoice_batch_check_users(invoices.mapped("invoice_batch_id"))
            invoices_pdf = self.prepare_invoices(invoices)
        else:
            raise UserError(_("Unexpected model '%s'" % model))

        if invoices_pdf:
            if not self.company_id.report_service_id:
                raise UserError(_("There's no report defined on invoice company"))
            report_action = self.company_id.report_service_id.report_action(
                invoices_pdf
            )
            invoices_pdf.write({"is_move_sent": True})
            return report_action
