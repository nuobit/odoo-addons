# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, exceptions


class LightingProductAttribute(models.Model):
    _name = 'lighting.product.attribute'
    _order = 'sequence,name'

    name = fields.Char(required=True)

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order")

    @api.model
    def _get_domain(self):
        model_id = self.env.ref('lighting.model_lighting_product').id
        return [('model_id', '=', model_id)]

    product_field_id = fields.Many2one(comodel_name='ir.model.fields',
                                       ondelete='restrict', string='Product field',
                                       domain=_get_domain,
                                       required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The attribute name must be unique!'),
                        ('product_field_uniq', 'unique (product_field_id)', 'The product_field must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product.group'].search([('attribute_ids', 'in', self.ids)])
        if records:
            raise exceptions.UserError(_("You are trying to delete a record that is still referenced!"))
        return super().unlink()
