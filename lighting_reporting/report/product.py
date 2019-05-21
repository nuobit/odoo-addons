# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductReport(models.AbstractModel):
    _name = 'report.lighting_reporting.report_product'

    @api.model
    def get_report_values(self, docids, data=None):
        # AccountPaymentOrderObj = self.env['account.payment.order']
        # docs = AccountPaymentOrderObj.browse(docids)
        # model = self.env.context.get('active_model')
        # docs = self.env[model].browse(self.env.context.get('active_id'))
        # report = self.env['ir.actions.report']._get_report_from_name('lighting_reporting.report_product')
        model = 'lighting.product'
        records = self.env[model].browse(docids)


        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': records,
        }
