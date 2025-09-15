# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class HrCourseAttendee(models.Model):
    _inherit = "hr.course.attendee"

    duration = fields.Float(
        string="Duration",
        related="course_schedule_id.duration",
        readonly=True,
        help="Duration in hours",
    )
