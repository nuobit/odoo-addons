# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import datetime

import math
import random

from .tzinterval import TzInterval


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

    @api.multi
    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        tasks = self.tasks_ids.filtered(lambda x: x.date_end)
        if tasks:
            self.tasks_ids.write({'date_deadline': max(tasks.mapped('date_end'))})
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)

        if not self.product_id.service_time:
            return res

        # initial date_start
        now = fields.datetime.now().replace(second=0, microsecond=0)
        quarters = now.minute / 15
        base_date_start = now + datetime.timedelta(minutes=round((math.ceil(quarters) - quarters) * 15))
        base_duration = int(round(self.product_id.service_time * 60))

        # check resources availability
        resources = self.env['resource.resource'].search([
            ('user_id.active', '!=', False),
            ('resource_type', '=', 'user'),
        ])
        if not resources:
            raise UserError(_("There's no active resources"))

        free_time_by_user = {}
        for r in resources:
            duration_task = int(round(base_duration / (r.time_efficiency / 100)))
            duration_td = datetime.timedelta(minutes=duration_task)
            cint = TzInterval(base_date_start, base_date_start + duration_td, tz=r.tz)

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
            rint = r.find_next_available(cint, project)
            if rint:
                free_time_by_user[r.user_id.id] = rint

        if not free_time_by_user:
            raise UserError(_("No candidates found, cannot validate order"))
        available_user_time = self._free_time_selection(free_time_by_user, project)

        res.update({
            'user_id': available_user_time[0],
            'date_start': available_user_time[1].date_start,
            'date_end': available_user_time[1].date_end,
        })

        return res
