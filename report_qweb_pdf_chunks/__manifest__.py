# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Report qweb PDF chunks",
    "summary": "This module temporarily splits all selected "
    "documents to print into chunks and invokes the external Wkhtmltopdf"
    " (0.12.5) program for each chunk to avoid the well known memory "
    "problems when printing many documents.",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "data/ir_config_parameter.xml",
    ],
}
