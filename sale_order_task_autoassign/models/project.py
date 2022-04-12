# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    department_ids = fields.Many2many(
        comodel_name="hr.department", string="Departments"
    )


class Task(models.Model):
    _inherit = "project.task"

    base_duration = fields.Float(compute="_compute_duration")

    def _compute_duration(self):
        for t in self:
            if t.date_start and t.date_end:
                duration_h = (t.date_end - t.date_start).seconds / 60 / 60
                if t.user_id:
                    resource = self.env["resource.resource"].search(
                        [("user_id", "=", t.user_id.id)]
                    )
                    if len(resource) > 1:
                        raise ValidationError(
                            _(
                                "More than one resource found assigned to the same user %s"
                                % t.user_id.name
                            )
                        )
                    if not resource:
                        raise ValidationError(
                            _(
                                "No resource found assigned to the user %s"
                                % t.user_id.name
                            )
                        )
                    duration_h *= resource.time_efficiency / 100
            else:
                if not t.sale_line_id:
                    raise ValidationError(
                        _("Task %s has no start and end date and no sale line" % t.name)
                    )
                duration_h = (
                    t.sale_line_id.product_id.service_time
                    * t.sale_line_id.product_uom_qty
                )
            t.base_duration = duration_h
