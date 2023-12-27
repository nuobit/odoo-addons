# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Base report json",
    "summary": "Base module to create json report",
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
            "report_json/static/src/js/report/action_manager_report.esm.js",
        ],
    },
}
