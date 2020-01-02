# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import base64


class AccountInvoiceBatchProcess(models.TransientModel):
    _name = "account.invoice.batch.process"

    @property
    def company_id(self):
        context = self.env.context or {}
        model = context.get('active_model')
        active_ids = context.get('active_ids')

        active_objects = self.env[model].browse(active_ids)
        company = active_objects.mapped('company_id')

        if model not in ('account.invoice.batch', 'account.invoice'):
            raise UserError(_("Unexpected model '%s'" % model))

        if len(company) > 1:
            raise UserError(_("More than one company found. The data selected must be of the same company"))

        return company

    invoice_batch_sending_pdf = fields.Boolean(string='PDF', default=True)
    invoice_batch_sending_email = fields.Boolean(string='E-mail', default=True)
    invoice_batch_sending_email_template_id = fields.Many2one(
        string="E-mail template",
        comodel_name='mail.template',
        domain=[('model_id', '=', 'account.invoice')],
        default=lambda self: self.company_id.default_invoice_batch_sending_email_template_id,
    )
    invoice_batch_sending_signedfacturae = fields.Boolean(string='Factura-e signed', default=True)
    invoice_batch_sending_unsignedfacturae = fields.Boolean(string='Factura-e unsigned', default=True)

    @api.multi
    def prepare_invoices(self, invoices):
        self.ensure_one()

        # facturae
        sending_facturae = list(
            filter(None, [
                self.invoice_batch_sending_signedfacturae and 'signedfacturae' or None,
                self.invoice_batch_sending_unsignedfacturae and 'unsignedfacturae' or None,
            ]))
        if sending_facturae:
            for inv in invoices.filtered(
                    lambda x: x.invoice_batch_sending_method in sending_facturae):
                if not inv.sent:
                    try:
                        invoice_file, file_name = inv.get_facturae(
                            inv.invoice_batch_sending_method == 'signedfacturae')

                        file = base64.b64encode(invoice_file)
                        self.env['ir.attachment'].create({
                            'name': file_name,
                            'datas': file,
                            'datas_fname': file_name,
                            'res_model': 'account.invoice',
                            'res_id': inv.id,
                            'mimetype': 'application/xml'
                        })
                        inv.sent = True
                    except:
                        pass

        # email
        if self.invoice_batch_sending_email:
            invoices = invoices.filtered(
                lambda x: x.invoice_batch_sending_method == 'email')
            invoices.message_post_with_template(
                self.invoice_batch_sending_email_template_id.id,
                message_type='email',
                composition_mode='mass_mail',
            )
            invoices.write({'sent': True})

        # pdf
        if self.invoice_batch_sending_pdf:
            return invoices.filtered(
                lambda x: x.invoice_batch_sending_method == 'pdf')

        return self.env['account.invoice']

    @api.multi
    def process_invoices(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        model = context.get('active_model')

        active_objects = self.env[model].browse(context.get('active_ids'))
        invoices_pdf = self.env['account.invoice']
        if model == 'account.invoice.batch':
            if not active_objects.mapped('unsent_invoice_ids'):
                raise UserError(_("There's no invoices to process"))
            for batch in active_objects:
                invoices = batch.unsent_invoice_ids
                invoices_pdf += self.prepare_invoices(invoices)
        elif model == 'account.invoice':
            if not active_objects:
                raise UserError(_("There's no invoices to process"))
            invoices = active_objects.filtered(lambda x: x.invoice_batch_id and not x.sent)
            invoices_pdf = self.prepare_invoices(invoices)
        else:
            raise UserError(_("Unexpected model '%s'" % model))

        if invoices_pdf:
            if not self.company_id.report_service_id:
                raise UserError(_("There's no report defined on invoice company"))
            if invoices_pdf:
                report_action = self.company_id.report_service_id.report_action(invoices_pdf)
                invoices_pdf.write({'sent': True})
                return report_action
