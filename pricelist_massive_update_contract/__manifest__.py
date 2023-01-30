# Copyright 2021 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Price List Massive Update Contract",
    "summary": "Update pricelists according to pricelist tags on contracts",
    "version": "14.0.1.0.1",
    "category": "Sale",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["pricelist_massive_update", "contract"],
    "data": [
        "views/pricelist_update.xml",
    ],
    "auto_install": False,
}
