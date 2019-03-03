# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from collections import OrderedDict


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    @api.multi
    def export_name(self, template_id=None):
        active_langs = ['en_US', 'es_ES', 'fr_FR']
        res = []
        for ta in template_id.attachment_ids.sorted(lambda x: x.sequence):
            prod_attachment_ids = self.filtered(lambda x: x.type_id.id == ta.type_id.id)
            if prod_attachment_ids.mapped('attachment_id'):
                attach_type_d = {}
                for pa in prod_attachment_ids:
                    if pa.type_id.code not in attach_type_d:
                        attach_type_d[pa.type_id.code] = {}
                        for lang in active_langs:
                            if 'label' not in attach_type_d[pa.type_id.code]:
                                attach_type_d[pa.type_id.code]['label'] = {}
                            attach_type_d[pa.type_id.code]['label'][lang] = pa.type_id.with_context(lang=lang).name
                    if 'value' not in attach_type_d[pa.type_id.code]:
                        attach_type_d[pa.type_id.code]['value'] = []

                    attach_type_d[pa.type_id.code]['value'].append({
                        'datas_fname': pa.datas_fname,
                        'store_fname': pa.attachment_id.store_fname,
                        'sequence': pa.sequence,
                    })
                res.append(attach_type_d)

        return res
