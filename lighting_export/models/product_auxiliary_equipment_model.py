# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class LightingProductAuxiliaryEquipmentModel(models.Model):
    _inherit = 'lighting.product.auxiliaryequipmentmodel'

    @api.multi
    def export_name(self):
        lang = self.env['res.lang'].search([('code', '=', self.env.user.lang)])
        res = []
        for rec in self:
            line = []
            if rec.reference:
                line.append(rec.reference)
            line.append(rec.brand_id.display_name)
            if rec.date:
                line.append(fields.Date.from_string(rec.date).strftime(lang.date_format))
            res.append(' - '.join(line))

        #TODO: acabar de veure com ho posem
        return ','.join(res)
