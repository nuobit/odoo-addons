# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class LightingProductBeamPhotometricDistribution(models.Model):
    _inherit = 'lighting.product.beam.photodistribution'

    @api.multi
    def export_name(self):
        res = []
        for rec in self:
            res.append(rec.display_name)

        return ','.join(res)
