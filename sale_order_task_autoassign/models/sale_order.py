# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import logging
import math
import random

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .tools import TzInterval

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _order = "id desc"

    task_user_id = fields.Many2one(
        string="Assigned to",
        comodel_name="res.users",
        ondelete="restrict",
        compute="_compute_task_user_id",
        search="_search_task_user_id",
        readonly=True,
    )

    def _compute_task_user_id(self):
        for rec in self:
            if rec.tasks_ids:
                rec.task_user_id = rec.tasks_ids[0].user_id
            else:
                rec.task_user_id = False

    def _search_task_user_id(self, op, value):
        tasks = self.env["project.task"].search(
            [("sale_line_id", "!=", False), ("user_id.name", op, value)]
        )
        return [("id", "in", tasks.mapped("sale_line_id.order_id").ids)]

    @api.depends(
        "order_line.customer_lead",
        "date_order",
        "order_line.state",
        "tasks_ids.date_end",
        "tasks_ids.date_deadline",
    )
    def _compute_expected_date(self):
        super(SaleOrder, self)._compute_expected_date()
        for order in self:
            tasks = order.tasks_ids.filtered(lambda x: x.date_end)
            if tasks:
                order.expected_date = max(tasks.mapped("date_end"))
            else:
                tasks = order.tasks_ids.filtered(lambda x: x.date_deadline)
                if tasks:
                    order.expected_date = (
                        pytz.timezone(self.env.user.tz)
                        .localize(
                            fields.Datetime.to_datetime(
                                max(tasks.mapped("date_deadline"))
                            )
                        )
                        .astimezone(pytz.utc)
                        .replace(tzinfo=None)
                    )
                else:
                    order.expected_date = False

    def _free_time_selection(self, free_time_by_user, project):
        now = fields.datetime.now().replace(tzinfo=None)
        tasks_per_user = self.env["project.task"].read_group(
            [
                ("project_id", "=", project.id),
                ("user_id", "in", tuple(free_time_by_user.keys())),
                ("date_start", "!=", False),
                ("date_end", "!=", False),
                ("date_end", ">", now),
            ],
            ["id"],
            ["user_id"],
            orderby="user_id",
        )
        tasks_count_per_user = {
            x["user_id"][0]: x["user_id_count"] for x in tasks_per_user
        }
        return sorted(
            free_time_by_user.items(),
            key=lambda x: (
                x[1].date_start,
                tasks_count_per_user.get(x[0], 0),
                x[1].duration,
                random.randrange(100),
            ),
        )[0]

    def _prepare_main_tasks(self):
        return self.tasks_ids

    def _calculate_available_user_time(self, duration_h, project_id):
        # initial date_start
        now = fields.datetime.now().replace(second=0, microsecond=0)
        date_ref = self.date_order > now and self.date_order or now
        quarters = date_ref.minute / 15
        base_date_start = date_ref + datetime.timedelta(
            minutes=round((math.ceil(quarters) - quarters) * 15)
        )
        base_duration = int(round(duration_h * 60))

        # check resources availability
        domain = [
            ("user_id.active", "!=", False),
            ("resource_type", "=", "user"),
            ("calendar_id.attendance_ids", "!=", False),
        ]
        calendar_ids = self.tasks_ids.mapped("project_id.resource_calendar_id").ids
        if calendar_ids:
            domain.append(("calendar_id", "in", calendar_ids))
        department_user_ids = self.tasks_ids.mapped(
            "project_id.department_ids.member_ids.user_id"
        )
        if department_user_ids:
            domain.append(("user_id", "in", department_user_ids.ids))

        resources = self.env["resource.resource"].search(domain)
        if not resources:
            raise UserError(_("No active resources found"))

        free_time_by_user = {}
        for r in resources:
            duration_task = int(round(base_duration / (r.time_efficiency / 100)))
            duration_td = datetime.timedelta(minutes=duration_task)
            cint = TzInterval(base_date_start, base_date_start + duration_td)

            # check durations: if it's ever possible to fit the cint duration
            # on at least one day, if not, stop searching going forward and
            # throw an error
            for a in r.calendar_id.attendance_ids:
                if a.hour_from < a.hour_to:
                    duration_slot = int(round((a.hour_to - a.hour_from) * 60))
                    if duration_slot >= duration_task:
                        break
            else:
                continue

            # find available date slot
            rint = r.find_next_available(cint, project_id)
            if rint:
                free_time_by_user[r.user_id.id] = rint

        if not free_time_by_user:
            raise UserError(_("No candidates found, cannot validate order"))
        available_user_time = self._free_time_selection(free_time_by_user, project_id)
        return available_user_time

    def _action_confirm(self):

        # TODO: self.with_context generates an error. If it's
        #  not commented, tasks won't be generated in tests
        # existing_task = self.tasks_ids
        # if existing_task:
        #     raise ValidationError(
        #         _(
        #             "Inconsistent data: Tasks %s already exists and cannot "
        #             "be overwritten. Please, delete this task before create it again"
        #             % existing_task.mapped("name")
        #         )
        #     )
        result = super(SaleOrder, self)._action_confirm()

        if not self.tasks_ids:
            return result

        main_tasks = self._prepare_main_tasks().sorted(
            lambda x: x.sale_line_id.product_id.service_time
            * x.sale_line_id.product_uom_qty
        )
        main_tasks_duration_h = sum(
            [
                x.sale_line_id.product_id.service_time * x.sale_line_id.product_uom_qty
                for x in main_tasks
            ]
        )
        longest_task = main_tasks[-1]
        other_tasks = (self.tasks_ids - longest_task).sorted(
            lambda x: (x.sale_line_id.sequence, x.sale_line_id.id)
        )
        longest_task.write(
            {
                "name": longest_task.name,
                "description": "\n".join(
                    ["<p>- %s</p>" % x.sale_line_id.name for x in other_tasks]
                ),
            }
        )
        other_tasks.write({"sale_line_id": False})
        other_tasks.unlink()

        available_user_time = self._calculate_available_user_time(
            main_tasks_duration_h, longest_task.project_id
        )

        longest_task.update(
            {
                "user_id": available_user_time[0],
                "date_start": available_user_time[1].date_start,
                "date_end": available_user_time[1].date_end,
            }
        )

        # assign the deadline of main task
        if longest_task.date_end:
            longest_task.write({"date_deadline": longest_task.date_end.date()})

        # bike_location
        if longest_task.bike_location != "na":
            # set the stage according to bike_location
            meta_type = None
            if longest_task.bike_location == "bring_in":
                meta_type = "bring_in"
            elif longest_task.bike_location == "in_shop":
                meta_type = "in_place"
            stage = self._get_stage_by_metatype(longest_task.project_id, meta_type)
            if stage:
                longest_task.stage_id = stage
        return result

    def _get_stage_by_metatype(self, project, meta_type):
        task_type = self.env["project.task.type"].search(
            [
                ("project_ids", "in", project.ids),
                ("meta_type", "=", meta_type),
            ]
        )
        if not task_type:
            raise ValidationError(_("Theres no stages with metatype %s" % meta_type))

        if len(task_type) > 1:
            raise UserError(
                _("The project '%s' has defined " "more than one stage %s of type '%s'")
                % (
                    project.name,
                    task_type.mapped("name"),
                    meta_type,
                )
            )
        return task_type

    def write(self, values):
        if "bike_location" in values:
            for task in self.tasks_ids:
                if values["bike_location"] in ("bring_in", "in_shop"):
                    new_meta_type = {
                        ("bring_in", "in_place"): "bring_in",
                        ("in_shop", "bring_in"): "in_place",
                    }.get((values["bike_location"], task.stage_id.meta_type))

                    if new_meta_type:
                        stage = self._get_stage_by_metatype(
                            task.project_id, new_meta_type
                        )
                        task.stage_id = stage
        result = super().write(values)
        return result
