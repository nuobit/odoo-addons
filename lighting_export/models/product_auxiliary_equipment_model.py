# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class LightingProductAuxiliaryEquipmentModel(models.Model):
    _inherit = 'lighting.product.auxiliaryequipmentmodel'

    @api.multi
    def export_name(self):
        res = []
        for rec in self:
            res.append("%s - %s" % (rec.reference, rec.brand_id.display_name))

        return ','.join(res)


    """reference = fields.Char(string='Reference')
    brand_id = fields.Many2one(comodel_name='lighting.product.auxiliaryequipmentbrand',
                               ondelete='restrict', string='Brand', required=True)
    date = fields.Date(string='Date')

    """