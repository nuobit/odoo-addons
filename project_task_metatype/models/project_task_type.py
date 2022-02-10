# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    meta_type = fields.Selection(
        selection=[
            ("done", "Done"),
            ("parking", "Parking"),
            ("bring_in", "Bring In"),
            ("in_place", "In Place"),
            ("to_assembly", "To Assembly"),
            ("cancel", "Cancel"),
        ]
    )

    @api.constrains("project_ids", "meta_type")
    def _check_meta_type_duplicated(self):
        for rec in self:
            if rec.meta_type:
                other = self.env["project.task.type"].search(
                    [
                        ("id", "!=", rec.id),
                        ("project_ids", "in", rec.project_ids.ids),
                        ("meta_type", "=", rec.meta_type),
                    ]
                )
                if other:
                    raise ValidationError(
                        _(
                            "There's other stage(s) %s with the same "
                            "type '%s' on the same project(s)"
                        )
                        % (other.mapped("name"), rec.meta_type)
                    )
