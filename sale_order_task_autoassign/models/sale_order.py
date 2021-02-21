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

    @api.multi
    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()

        # initial date_start
        now = fields.datetime.now().replace(second=0, microsecond=0)
        date_ref = self.date_order > now and self.date_order or now
        quarters = date_ref.minute / 15
        base_date_start = date_ref + datetime.timedelta(minutes=round((math.ceil(quarters) - quarters) * 15))

        # tasks to allocate
        tasks_to_allocate = TaskList([
            Task(
                task,
                base_date_start,
                duration=int(round(task.sale_line_id.product_id.service_time * 60))
            ) for task in self.tasks_ids.filtered(
                lambda x: x.sale_line_id.product_id.service_time > 0)
        ])
        if tasks_to_allocate:
            # get resource candidates for that tasks
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

            # calculate the tasks by user
            max_it = int(self.env['ir.config_parameter'].get_param('sale_order_task_autoassign.max_it', 200))
            _logger.info("Maximum iterations established to %i" % max_it)
            candidate_usertasks = self._allocate_tasks(tasks_to_allocate, resources, max_it=max_it)
            if not candidate_usertasks:
                raise UserError(_("No available resources found, cannot validate the order"))

            # choose only one of the candidates
            t = random.randrange(0, len(candidate_usertasks))
            resource_id, ctasklist = list(candidate_usertasks.tasks.items())[t]
            user = candidate_usertasks.resources[resource_id].user_id
            for e in ctasklist.tasks:
                task = e.obj
                task.write({
                    'user_id': user.id,
                    'date_start': e.start,
                    'date_end': e.end,
                })

            # assign the deadline of each task
            tasks = self.tasks_ids.filtered(lambda x: x.date_end)
            if tasks:
                self.tasks_ids.write({'date_deadline': max(tasks.mapped('date_end'))})

        return result

    def _allocate_tasks(self, src_tasks, resources, max_it=None):
        N = len(src_tasks)
        it = 0

        now = fields.datetime.now().replace(tzinfo=None)
        current_tasks = self.env['project.task'].search([
            ('user_id', 'in', resources.mapped('user_id.id')),
            ('date_start', '!=', False),
            ('date_end', '!=', False),
            ('date_end', '>', now)
        ])
        tasks_by_user = {}
        for ct in current_tasks:
            tasks_by_user.setdefault(ct.user_id.id, []).append(TzInterval(ct.date_start, ct.date_end))

        def _allocate_tasks0(src_tasks, current_usertasks=UserTasks(), candidate_usertasks=None, level=0):
            nonlocal it
            it += 1
            if candidate_usertasks and max_it and it >= max_it:
                return candidate_usertasks

            if not src_tasks:
                candidate_usertasks1 = current_usertasks.get_quickest(N)
                if candidate_usertasks:
                    if candidate_usertasks < candidate_usertasks1:
                        candidate_usertasks1 = candidate_usertasks.copy()
                    elif candidate_usertasks == candidate_usertasks1:
                        candidate_usertasks1 = candidate_usertasks.merge(candidate_usertasks1)

                return candidate_usertasks1
            else:
                for i in range(len(src_tasks)):
                    task_base_root, task_base_children = src_tasks.rotate_split(i)
                    current_usertasks2 = current_usertasks.copy()
                    for r in current_usertasks.get_resources() or resources:
                        tsk = task_base_root.copy()
                        tsk.update_duration(r.time_efficiency / 100, is_rate=True)
                        if r.is_allocatable(tsk.interval):
                            cint = r.find_next_available(tsk.interval, current_usertasks2.get(r), tasks_by_user)
                            if not cint:
                                current_usertasks2.del_user(r)
                            else:
                                tsk_avail = Task(tsk.obj, cint.date_start, cint.date_end)
                                current_usertasks2.add(r, tsk_avail)
                                if (candidate_usertasks and current_usertasks2.get(r).end >= candidate_usertasks.end):
                                    current_usertasks2.del_user(r)
                        else:
                            current_usertasks2.del_user(r)

                    if current_usertasks2:
                        candidate_usertasks = _allocate_tasks0(task_base_children, current_usertasks2,
                                                               candidate_usertasks, level + 1)
                return candidate_usertasks

        return _allocate_tasks0(src_tasks)
