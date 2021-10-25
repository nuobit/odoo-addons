# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project Task hide tasks",
    "version": "12.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Kilian Niubo",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit",
    "summary": "This module hides the tasks when their stage is done or canceled.",
    "depends": [
        "project_task_metatype",
    ],
    "data": [
        "views/project_task_views.xml",
    ],
    "installable": True,
}
