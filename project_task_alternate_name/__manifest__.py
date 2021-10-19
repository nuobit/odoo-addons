# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project task alternate name",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Kilian Niubo",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit",
    "summary": "This module generates a name based on partner, description,"
    "sale order name and the bike location."
    "It's shown on project calendar view.",
    "depends": [
        "project_task_bike_location",
    ],
    "data": [
        "views/product_category_views.xml",
        "views/sale_order_views.xml",
        "views/product_template_views.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
}
