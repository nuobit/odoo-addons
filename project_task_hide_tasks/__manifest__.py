# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project Task hide tasks",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Kilian Niubo",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit",
    "summary": "This module adds a check box to indicate in which states we want "
    "the tasks to be hidden in the calendar view.",
    "depends": [
        "project",
    ],
    "data": ["views/project_task_views.xml", "views/project_task_type_views.xml"],
    "installable": True,
}
