# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2022 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Report GS1 barcodes",
    "summary": "This module adds a GS1-128 and GS1-Datamatrix barcode format support",
    "version": "14.0.1.0.1",
    "category": "Reporting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "pystrich",
        ],
    },
    "depends": ["base"],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
    "auto_install": False,
}
