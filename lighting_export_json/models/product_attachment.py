# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from collections import OrderedDict

from .mixin import LightingExportJsonMixin


class LightingAttachment(models.Model, LightingExportJsonMixin):
    _inherit = 'lighting.attachment'

    @api.multi
    def export_json(self, template_id=None):
        valid_field = ['sequence', 'type_id', 'datas_fname']
        translate_field = ['type_id']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            if rec.type_id.id in template_id.attachment_ids.mapped("type_id.id"):
                line = OrderedDict()
                for field in valid_field:
                    field_d = rec.get_field_d(field, template_id, translate=field in translate_field)
                    if field_d:
                        line[field] = field_d['value']

                if rec.attachment_id:
                    line.update({
                        'store_fname': rec.attachment_id.store_fname,
                    })

                if line:
                    res.append(line)

        return res
