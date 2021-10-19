# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project Task Bike Location",
    "version": "12.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit",
    "summary": "This module links Task Bike Location to sale order and "
    "creates the tasks with the Bike Location in its name.",
    "depends": [
        "sale_timesheet",
        "sale_order_bike_location",
    ],
    "data": [
        "views/project_task_views.xml",
    ],
    "installable": True,
}
