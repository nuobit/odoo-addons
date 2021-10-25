# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale order task autoassign",
    "version": "12.0.1.1.10",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit",
    "summary": "This module allows creating tasks from sale orders with "
    "the duration defined on the service product. It also auto "
    "assigns the task to availableresources avoiding collisions "
    "and respecting the resources and leaves.",
    "depends": [
        "project_task_bike_location",
        "project_task_metatype",
        "product_service_time",
        "project_timeline_calendar",
    ],
    "data": [
        "views/project_views.xml",
        "views/sale_views.xml",
    ],
    "installable": True,
}
