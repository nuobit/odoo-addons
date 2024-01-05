# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector ERTransit / Erhardt",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "requests",
            "lxml",
        ],
    },
    "depends": [
        "connector",
    ],
    "data": [
        "views/backend_views.xml",
        "views/menus.xml",
        "templates/ertransit_template.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
