# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project timeline default view",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module allows to define what projects should open the"
    " timeline view from the default kanban view.",
    "depends": [
        "project_timeline",
    ],
    "data": [
        "views/project_views.xml",
    ],
    "installable": True,
}
