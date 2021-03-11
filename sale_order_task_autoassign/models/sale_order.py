# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import datetime
import math
import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .tools import TzInterval, TaskList, Task, UserTasks

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('order_line.customer_lead', 'confirmation_date', 'order_line.state')
    def _compute_expected_date(self):
        super(SaleOrder, self)._compute_expected_date()
        for order in self:
            tasks = order.tasks_ids.filtered(lambda x: x.date_end)
            if tasks:
                order.expected_date = max(tasks.mapped('date_end'))

    def _free_time_selection(self, free_time_by_user, project):
        now = fields.datetime.now().replace(tzinfo=None)
        tasks_per_user = self.env['project.task'].read_group([
            ('project_id', '=', project.id),
            ('user_id', 'in', tuple(free_time_by_user.keys())),
            ('date_start', '!=', False),
            ('date_end', '!=', False),
            ('date_end', '>', now),
        ], ['id'], ['user_id'], orderby='user_id')
        tasks_count_per_user = {x['user_id'][0]: x['user_id_count'] for x in tasks_per_user}
        return sorted(free_time_by_user.items(), key=lambda x: (
            x[1].date_start,
            tasks_count_per_user.get(x[0], 0),
            x[1].duration,
            random.randrange(100),
        ))[0]

    def _prepare_main_tasks(self):
        return self.tasks_ids

    @api.multi
    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()

        if not self.tasks_ids:
            return result

        main_tasks = self._prepare_main_tasks().sorted(
            lambda x: x.sale_line_id.product_id.service_time * x.sale_line_id.product_uom_qty)
        main_tasks_duration_h = sum([
            x.sale_line_id.product_id.service_time * x.sale_line_id.product_uom_qty
            for x in main_tasks])
        longest_task = main_tasks[-1]
        other_tasks = (self.tasks_ids - longest_task).sorted(
            lambda x: (x.sale_line_id.sequence, x.sale_line_id.id)
        )
        longest_task.write({
            'name': longest_task.name,
            'description': '\n'.join(['<p>- %s</p>' % x.sale_line_id.name for x in other_tasks]),
        })
        other_tasks.write({
            'sale_line_id': False
        })
        other_tasks.unlink()

        # initial date_start
        now = fields.datetime.now().replace(second=0, microsecond=0)
        date_ref = self.date_order > now and self.date_order or now
        quarters = date_ref.minute / 15
        base_date_start = date_ref + datetime.timedelta(minutes=round((math.ceil(quarters) - quarters) * 15))
        base_duration = int(round(main_tasks_duration_h * 60))

        # check resources availability
        domain = [
            ('user_id.active', '!=', False),
            ('resource_type', '=', 'user'),
            ('calendar_id.attendance_ids', '!=', False),
        ]
        calendar_ids = self.tasks_ids.mapped('project_id.resource_calendar_id').ids
        if calendar_ids:
            domain.append(('calendar_id', 'in', calendar_ids))
        department_user_ids = self.tasks_ids.mapped('project_id.department_ids.member_ids.user_id')
        if department_user_ids:
            domain.append(('user_id', 'in', department_user_ids.ids))

        resources = self.env['resource.resource'].search(domain)
        if not resources:
            raise UserError(_("No active resources found"))

        free_time_by_user = {}
        for r in resources:
            duration_task = int(round(base_duration / (r.time_efficiency / 100)))
            duration_td = datetime.timedelta(minutes=duration_task)
            cint = TzInterval(base_date_start, base_date_start + duration_td)

            # check durations: if it's ever possible to fit the cint duration
            # on at least one day, if not, stop searching going forward and throw an error
            for a in r.calendar_id.attendance_ids:
                if a.hour_from < a.hour_to:
                    duration_slot = int(round((a.hour_to - a.hour_from) * 60))
                    if duration_slot >= duration_task:
                        break
            else:
                continue

            # find available date slot
            rint = r.find_next_available(cint, longest_task.project_id)
            if rint:
                free_time_by_user[r.user_id.id] = rint

        if not free_time_by_user:
            raise UserError(_("No candidates found, cannot validate order"))
        available_user_time = self._free_time_selection(free_time_by_user, longest_task.project_id)

        longest_task.update({
            'user_id': available_user_time[0],
            'date_start': available_user_time[1].date_start,
            'date_end': available_user_time[1].date_end,
        })

        # assign the deadline of main task
        if longest_task.date_end:
            longest_task.write({'date_deadline': longest_task.date_end})

        return result
