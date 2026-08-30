# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "HR Course Duration",
    "summary": "This module adds a duration field in courses",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["hr_course"],
    "data": [
        "views/hr_course_form_view.xml",
        "views/hr_course_schedule_views.xml",
        "views/hr_course_attendee_views.xml",
    ],
}
