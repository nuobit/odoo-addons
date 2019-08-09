# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LightingReportingProductDatasheetWizard(models.TransientModel):
    _name = "lighting.reporting.product.datasheet.wizard"

    def _default_lang_id(self):
        lang = self.env.context.get('lang')
        if lang:
            return self.env['res.lang'].search([('code', '=', lang)]).id
        return False

    lang_id = fields.Many2one(string='Language', comodel_name='res.lang', required=True, default=_default_lang_id)

    @api.multi
    def print_product_datasheet(self):
        data = {
            'ids': self.env.context.get('active_ids'),
            'model': self.env.context.get('active_model'),
            'lang': self.lang_id.code,
        }

        return self.env.ref('lighting_reporting.action_report_product') \
            .report_action(self, data=data)
