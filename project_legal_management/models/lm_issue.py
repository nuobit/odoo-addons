# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class LMIssue(models.Model):
    _name = 'lm.issue'
    _parent_name = 'parent_id'
    _inherit = 'lm.tree.mixin'

    name = fields.Char(required=True)
    parent_id = fields.Many2one(comodel_name='lm.issue')

    complete_chain_ids = fields.Many2many(
        string="Complete Chain",
        comodel_name='lm.issue',
        compute='_compute_complete_chain_ids',
    )
