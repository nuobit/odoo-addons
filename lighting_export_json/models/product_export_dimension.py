# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, _
from collections import OrderedDict

from .mixin import LightingExportJsonMixin


class LightingProductExportDimension(LightingExportJsonMixin):

    @api.multi
    def export_name(self, template_id=None):
        valid_field = ['sequence', 'type_id', 'value']
        translate_field = ['type_id']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_d = rec.get_field_d(field, template_id, translate=field in translate_field)

                if field_d:
                    line[field] = field_d

            if line:
                res.append(line)

        return res
