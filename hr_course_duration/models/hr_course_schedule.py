# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrCourseSchedule(models.Model):
    _inherit = "hr.course.schedule"

    duration = fields.Float(help="Duration in hours")
