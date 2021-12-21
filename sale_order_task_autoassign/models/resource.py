# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import models

from .tools import TzInterval


class ResourceResource(models.Model):
    _inherit = "resource.resource"

    def is_allocatable(self, cint):
        # check durations: if it's ever possible to fit the cint duration
        # on at least one day, if not, exclude user
        cint_duration = int(round(cint.duration.seconds / 60))
        for a in self.calendar_id.attendance_ids:
            if a.hour_from < a.hour_to:
                duration_slot = int(round((a.hour_to - a.hour_from) * 60))
                if duration_slot >= cint_duration:
                    return True

        return False

    def get_next_attendance(self, cint):
        """ return next attendance period from datetime dt"""
        self.ensure_one()
        for a in self.calendar_id.attendance_ids.filtered(
            lambda x: int(x.dayofweek) == cint.weekday(self.tz)
        ).sorted(lambda x: x.hour_from):
            vint = TzInterval(
                a.date_from,
                a.date_to,
                tz=self.calendar_id.tz,
                base_tz=self.calendar_id.tz,
                to_tz=self.tz,
            )
            if cint.is_included(vint):
                dint_date_start_tz = cint.date_start_tz(self.tz).replace(
                    hour=int(a.hour_from),
                    minute=round((a.hour_from - int(a.hour_from)) * 60),
                )
                dint = TzInterval(
                    dint_date_start_tz,
                    datetime.timedelta(
                        minutes=int(round((a.hour_to - a.hour_from) * 60))
                    ),
                    tz=self.tz,
                )
                if cint.date_start < dint.date_end:
                    return dint
        return None

    def find_next_available(self, cint, project):
        """ get the next free periode after (cint) of the resource (r) """
        self.ensure_one()
        if not self.calendar_id.attendance_ids:
            return None

        att = self.get_next_attendance(cint)
        if not att:
            cint1_date_start_tz = (
                cint.date_start_tz(self.tz) + datetime.timedelta(days=1)
            ).replace(minute=0, hour=0)
            cint1 = TzInterval(cint1_date_start_tz, cint.duration, tz=self.tz)
            return self.find_next_available(cint1, project)
        else:
            if cint.is_included(att):
                # global and user leaves
                for gl in self.calendar_id.leave_ids.sorted(lambda x: x.date_from):
                    if gl.date_from < gl.date_to:
                        if not gl.resource_id or gl.resource_id == self:
                            gint = TzInterval(
                                gl.date_from,
                                gl.date_to,
                                base_tz=self.calendar_id.tz,
                                to_tz=self.tz,
                            )
                            if cint.is_overlaped(gint):
                                return self.find_next_available(
                                    cint.copy(gint.date_end), project
                                )
                else:
                    overlaped_tasks = self.env["project.task"].search(
                        [
                            ("project_id", "=", project.id),
                            ("user_id", "=", self.user_id.id),
                            ("date_start", "!=", False),
                            ("date_end", "!=", False),
                            ("date_end", ">", cint.date_start),
                            ("date_start", "<", cint.date_end),
                        ],
                        order="date_start",
                        limit=1,
                    )
                    if overlaped_tasks:
                        return self.find_next_available(
                            cint.copy(overlaped_tasks[0].date_end), project
                        )
                    else:
                        return cint
            else:
                if cint.starts_before(att):
                    return self.find_next_available(cint.copy(att.date_start), project)
                else:
                    return self.find_next_available(cint.copy(att.date_end), project)
