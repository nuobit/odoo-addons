# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductAbstractDimension(models.AbstractModel):
    _name = 'lighting.product.dimension.abstract'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    @api.multi
    def get_dimension_display(self):
        if self:
            same_uom = True
            uoms = set()
            for rec in self:
                if rec.type_id.uom not in uoms:
                    if not uoms:
                        uoms.add(rec.type_id.uom)
                    else:
                        same_uom = False
                        break

            res_label = ' x '.join(['%s' % x.type_id.name for x in self])
            res_value = ' x '.join(['%g' % x.value for x in self])

            if same_uom:
                res_label = '%s (%s)' % (res_label, uoms.pop())
            else:
                res_value = ' x '.join(['%g%s' % (x.value, x.type_id.uom) for x in self])

            return '%s: %s' % (res_label, res_value)

        return False


class LightingProductDimension(models.Model):
    _name = 'lighting.product.dimension'
    _inherit = 'lighting.product.dimension.abstract'


class LightingProductRecessDimension(models.Model):
    _name = 'lighting.product.recessdimension'
    _inherit = 'lighting.product.dimension.abstract'
