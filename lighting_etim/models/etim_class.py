# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingETIMClass(models.Model):
    _name = 'lighting.etim.class'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)
    version = fields.Integer("Version", required=True)
    change_code = fields.Char("Change code", required=True)

    status = fields.Char("Status", required=True)

    group_id = fields.Many2one(comodel_name='lighting.etim.group', ondelete='restrict', string='Group', required=True)

    synonim_ids = fields.One2many(comodel_name='lighting.etim.class.synonim',
                                  inverse_name='class_id', string='Synonims')

    feature_ids = fields.One2many(comodel_name='lighting.etim.class.feature',
                                  inverse_name='class_id', string='Features')

    _sql_constraints = [('code', 'unique (code)', 'The code must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals


class LightingETIMClassSynonim(models.Model):
    _name = 'lighting.etim.class.synonim'

    name = fields.Char("Synonim", required=True, translate=True)

    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='cascade', string='Class')
