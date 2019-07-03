# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingDimensionType(models.Model):
    _name = 'lighting.dimension.type'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    uom = fields.Char(string='Uom', help='Unit of mesure')
    description = fields.Char(string='Internal description')

    _sql_constraints = [('name_uniq', 'unique (name, uom)', 'The dimension name must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.name, record.uom)
            vals.append((record.id, name))

        return vals
