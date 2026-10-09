# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Restricted Timesheet",
    "summary": "Hide the timesheets of restricted tasks outside their group",
    "version": "15.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["project_task_restricted", "hr_timesheet"],
    "data": ["security/project_task_restricted_hr_timesheet_security.xml"],
    "auto_install": True,
}
