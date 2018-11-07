# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingETIMGroup(models.Model):
    _name = 'lighting.etim.group'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)

    _sql_constraints = [('code', 'unique (code)', 'The code must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals
