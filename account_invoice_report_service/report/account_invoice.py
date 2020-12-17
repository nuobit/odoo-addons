# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoiceServiceReport(models.AbstractModel):
    _name = 'report.account_invoice_report_service.report_invoice_service'

    @api.model
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('account_invoice_report_service.report_invoice_service')

        paperformat = report.paperformat_id
        header_max_height = paperformat.dpi / 25.4 * \
                            paperformat.header_spacing * 1.25

        docs = self.env[report.model].browse(docids)
        data = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'header_max_height': header_max_height,
        }

        return data


class AccountInvoiceDeliveryReport(models.AbstractModel):
    _name = 'report.account_invoice_report_service.report_invoice_delivery'

    @api.model
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('account_invoice_report_service.report_invoice_delivery')

        paperformat = report.paperformat_id
        header_max_height = paperformat.dpi / 25.4 * \
                            paperformat.header_spacing * 1.25

        docs = self.env[report.model].browse(docids)
        data = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'header_max_height': header_max_height,
        }

        return data
