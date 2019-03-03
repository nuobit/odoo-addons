# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s' % (field.field_description, )))
        return res
