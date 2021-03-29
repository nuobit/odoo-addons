# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project timeline calendar",
    "version": "12.0.2.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/pms",
    "summary": "This module adds a new calendar view on project tasks and places "
    "the tasks from the start and end date point of view, allowing to "
    "move them and change its duration.",
    "depends": [
        "project",
    ],
    "data": [
        "views/project_task_views.xml",
    ],
    "installable": True,
}
