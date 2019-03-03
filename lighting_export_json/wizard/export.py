# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.http import content_disposition, route, request

from io import BytesIO

import json


class LightingExport(models.TransientModel):
    _inherit = "lighting.export"

    output_type = fields.Selection(selection_add=[('export_product_json', _('Json file (.json)'))])

    @api.multi
    def export_product_json(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.report',
            'report_name': 'lighting_export_json.export_product_json',
            'report_type': 'json',
            'data': {'interval': self.interval,
                     'hide_empty_fields': self.hide_empty_fields,
                     'template_id': self.template_id.id,
                     'active_ids': self.env.context.get('active_ids'),
                     'lang': self.lang_id.code,
                     },
        }
