# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2022 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Report GS1 barcodes",
    "summary": "This module adds a GS1-128 and GS1-Datamatrix barcode format support",
    "version": "17.0.1.0.0",
    "category": "Reporting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "pystrich",
        ],
    },
    "depends": ["base"],
    "maintainers": ["eantones"],
}
