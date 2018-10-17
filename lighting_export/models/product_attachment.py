# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    @api.multi
    def export_name(self, template_id=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        res = []
        for ta in template_id.attachment_ids.sorted(lambda x: x.sequence):
            prod_attachment_ids = self.filtered(lambda x: x.type_id.id == ta.type_id.id)
            if prod_attachment_ids.mapped('attachment_id'):
                pattern_l = ['%s/web/image/%i']
                if ta.resolution:
                    pattern_l.append(ta.resolution)
                pattern_l.append('%s')
                for pa in prod_attachment_ids:
                    type_meta = pa.fields_get(['type_id'], ['string'])['type_id']
                    res.append([(type_meta['string'], pa.type_id.display_name),
                                ('URL', ('/'.join(pattern_l) % (base_url, pa.attachment_id.id, pa.datas_fname))),
                                ])
        return res
