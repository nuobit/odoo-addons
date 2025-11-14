# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Price List Massive Update Contract",
    "summary": "Update pricelists according to pricelist tags on contracts",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["pricelist_massive_update", "contract"],
    "data": [
        "views/pricelist_update.xml",
    ],
    "auto_install": False,
}
