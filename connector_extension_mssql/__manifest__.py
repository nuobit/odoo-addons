# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector Extension MSSQL",
    "summary": "This module extends the connector extension module to "
    "add support for Microsoft SQL databases.",
    "version": "18.0.1.0.1",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "external_dependencies": {
        "python": [
            "pymssql<=2.2.5 ; python_version <= '3.10'",
            "pymssql<=2.2.8 ; python_version < '3.12'",
            "pymssql<=2.3.7 ; python_version >= '3.12'",
        ],
    },
    "depends": ["connector_extension_sql"],
}
