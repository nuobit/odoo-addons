# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RatingRating(models.Model):
    _inherit = "rating.rating"

    # for the record rule on ratings, which every internal user can list
    restricted = fields.Boolean(
        compute="_compute_restricted",
        search="_search_restricted",
        groups="project_task_restricted.group_restricted_task",
    )

    def _compute_restricted(self):
        Task = self.env["project.task"]
        for rating in self:
            rating.restricted = bool(
                Task._restricted_task_of(rating.res_model, rating.res_id)
            )

    def _search_restricted(self, operator, value):
        return self.env["project.task"]._restricted_reference_search(
            "res_model", "res_id", operator, value
        )
