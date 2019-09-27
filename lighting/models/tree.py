# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingTreeMixin(models.AbstractModel):
    _name = 'lighting.tree.mixin'

    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                search='_search_complete_name')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = '%s / %s' % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    def _search_complete_name(self, operator, value):
        return [('name', operator, value)]

    child_count = fields.Integer(compute='_compute_child_count', string='Childs')

    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    level = fields.Integer(string='Level', readonly=True, compute='_compute_level')

    def _get_level(self):
        self.ensure_one()
        if not self.parent_id:
            return 0
        else:
            return self.parent_id._get_level() + 1

    def _compute_level(self):
        for rec in self:
            rec.level = rec._get_level()

    def _get_root(self):
        self.ensure_one()
        if not self.parent_id:
            return self
        else:
            return self.parent_id._get_root()
