# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models, fields
from odoo.exceptions import UserError, ValidationError

import datetime

import json
import re


class ExportProductJson(models.AbstractModel):
    _name = 'report.lighting_export_json.export_product_json'
    _inherit = 'report.report_json.abstract'

    def generate_json_report(self, data, objects):
        template_id = self.env['lighting.export.template'].browse(data.get('template_id'))
        objects = self.env['lighting.product'].browse(data.get('active_ids'))
        if data.get('interval') == 'all':
            active_model = self.env.context.get('active_model')
            active_domain = data.get('context').get('active_domain')
            objects = self.env[active_model].search(active_domain)

        res = template_id.generate_data(objects, hide_empty_fields=data.get('hide_empty_fields'))

        def default(o):
            if isinstance(o, datetime.date):
                return fields.Date.to_string(o)

            if isinstance(o, datetime.datetime):
                return fields.Datetime.to_string(o)

            if isinstance(o, set):
                return sorted(list(o))

        kwargs = {}
        if data['pretty_print']:
            kwargs = dict(indent=4, sort_keys=True)

        return json.dumps(res, ensure_ascii=False, default=default, **kwargs)
