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
        now = fields.datetime.now()
        date_ref = (self.date_order > now and self.date_order or now).replace(
            second=0, microsecond=0
        )
        quarters = date_ref.minute / 15
        base_date_start = date_ref + datetime.timedelta(
            minutes=round((math.ceil(quarters) - quarters) * 15),
        )
        base_duration = int(round(duration_h * 60))

        # check resources availability
        domain = [
            ("user_id.active", "!=", False),
            ("resource_type", "=", "user"),
            ("calendar_id.attendance_ids", "!=", False),
        ]
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

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        if self.date_order:
            res["date_order"] = self.date_order
        return res

    def _prepare_other_tasks_duration(self, tasks):
        return sum(tasks.mapped("base_duration"))

    def _update_tasks(self, longest_task, longest_task_duration_h):
        other_tasks = (self.tasks_ids - longest_task).sorted(
            lambda x: (x.sale_line_id.sequence, x.sale_line_id.id)
        )
        other_task_duration_h = self._prepare_other_tasks_duration(other_tasks)
        for t in other_tasks:
            if t.sale_line_id:
                t.description = t.sale_line_id.name.replace("\n", "<br>")
        longest_task.description = "<br>".join(
            filter(None, [longest_task.description] + other_tasks.mapped("description"))
        )
        other_tasks.write({"sale_line_id": False})
        other_tasks.unlink()
        longest_task.write(
            {
                "date_start": False,
                "date_end": False,
            }
        )
        available_user_time = self._calculate_available_user_time(
            longest_task_duration_h + other_task_duration_h, longest_task.project_id
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
            elif longest_task.bike_location == "to_assembly":
                meta_type = "to_assembly"
            stage = self._get_stage_by_metatype(longest_task.project_id, meta_type)
            if stage:
                longest_task.stage_id = stage

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        main_tasks = self._prepare_main_tasks()
        if main_tasks:
            longest_task = main_tasks.sorted(lambda x: x.base_duration)[-1]
            longest_task_duration_h = longest_task.base_duration
            self._update_tasks(longest_task, longest_task_duration_h)
        return result

    def _get_stage_by_metatype(self, project, meta_type):
        if meta_type:
            task_type = self.env["project.task.type"].search(
                [
                    ("project_ids", "in", project.ids),
                    ("meta_type", "=", meta_type),
                ]
            )
            if not task_type:
                raise ValidationError(
                    _("Theres no stages with metatype %s" % meta_type)
                )

            if len(task_type) > 1:
                raise UserError(
                    _(
                        "The project '%s' has defined "
                        "more than one stage %s of type '%s'"
                    )
                    % (
                        project.name,
                        task_type.mapped("name"),
                        meta_type,
                    )
                )
            return task_type
        return self.env["project.task.type"]

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
                elif values["bike_location"] == "to_assembly":
                    stage = self._get_stage_by_metatype(task.project_id, "to_assembly")
                    task.stage_id = stage

        result = super().write(values)
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        # to avoid reentering in nested line creation
        if not self.env.context.get("main_lines", True):
            return super().create(vals_list)
        order_group = {}
        for val in vals_list:
            order_id = val.get("order_id")
            if not order_id:
                raise ValidationError(
                    _("Order id is None or is not on the lines to create")
                )
            order_group.setdefault(order_id, []).append(val)
        lines = self.browse()
        for order_id, vals_list in order_group.items():
            order = self.env["sale.order"].browse(order_id)
            existing_tasks = order._prepare_main_tasks()
            # merge the existing tasks if they exist
            longest_task, longest_task_duration_h = self.env["project.task"], None
            if existing_tasks:
                longest_task = existing_tasks.sorted(lambda x: x.base_duration)[-1]
                longest_task_duration_h = longest_task.base_duration
                existing_other_tasks = existing_tasks - longest_task
                if existing_other_tasks:
                    longest_task.description = "<br>".join(
                        filter(
                            None,
                            [longest_task.description]
                            + existing_other_tasks.mapped("description"),
                        )
                    )
                    longest_task_duration_h += sum(
                        existing_other_tasks.mapped("base_duration")
                    )
                    existing_other_tasks.write({"sale_line_id": False})
                    existing_other_tasks.unlink()
            order_lines = super(
                SaleOrderLine, self.with_context(main_lines=False)
            ).create(vals_list)
            lines |= order_lines
            main_tasks = order._prepare_main_tasks()
            if main_tasks:
                if not longest_task:
                    longest_task = main_tasks.sorted(lambda x: x.base_duration)[-1]
                    longest_task_duration_h = longest_task.base_duration
                order._update_tasks(longest_task, longest_task_duration_h)
        return lines
