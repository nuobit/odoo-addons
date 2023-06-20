# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector Extension MySQL",
    "summary": "This module extends the connector extension module "
    "to add support for MySQL databases.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "mysql-connector-python==8.0.31",
        ],
    },
    "depends": ["connector_extension_sql"],
}
