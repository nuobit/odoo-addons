# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LightingExport(models.TransientModel):
    _name = "lighting.export"
    _description = "Export data"

    @api.multi
    def export_product_xlsx(self):
        self.ensure_one()

        #active_ids = self._context.get('active_ids')
        #active_model = self._context.get('active_model')
        #product_ids = self.env[active_model].browse(active_ids)

        a=1

        context = dict(self.env.context,
                       active_ids=self.env.context.get('active_ids'))

        return {
            'name': 'Lighting product XLSX report',
            'model': 'lighting.product',
            'type': 'ir.actions.report',
            'report_name': 'lighting_export.export_product_xlsx',
            'report_type': 'xlsx',
            'report_file': 'export.product',
            'context': context,
        }