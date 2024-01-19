# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "CBL Connector",
    "description": "Connector to get tracking info from CBL",
    "version": "11.0.0.1.2",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "requests",
            "lxml",
            "json",
        ],
    },
    "depends": [
        "connector",
    ],
    "data": [
        "views/backend_views.xml",
        "views/menus.xml",
        "templates/cbl_template.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
