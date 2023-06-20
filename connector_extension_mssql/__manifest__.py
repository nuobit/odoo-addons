# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector Extension MSSQL",
    "summary": "This module extends the connector extension module to "
    "add support for Microsoft SQL databases.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "pymssql",
        ],
    },
    "depends": ["connector_extension_sql"],
}
