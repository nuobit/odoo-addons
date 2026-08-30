# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LMResolution(models.Model):
    _name = "lm.resolution"
    _parent_name = "parent_id"
    _inherit = "lm.tree.mixin"
    _description = "LMResolution"

    name = fields.Char(required=True)
    parent_id = fields.Many2one(comodel_name="lm.resolution")

    complete_chain_ids = fields.Many2many(
        string="Complete Chain",
        comodel_name="lm.resolution",
        compute="_compute_complete_chain_ids",
    )
