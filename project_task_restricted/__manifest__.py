# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Restricted",
    "summary": "Restrict marked tasks to the members of a group",
    "version": "15.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["project"],
    "data": [
        "security/project_task_restricted_security.xml",
        "views/project_task_views.xml",
    ],
}
