# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Web notebook wrap",
    "summary": "This module inherit from notebook to wrap the content",
    "author": "NuoBiT Solutions SL",
    "category": "Reporting",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [],
    },
    "depends": [
        "base",
        "web",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "web_notebook_wrap/static/src/core/**/*",
        ],
    },
}
