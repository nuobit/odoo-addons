# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS sale order note line",
    "summary": "This module extends the functionality of pos restaurant and quotation"
               "to allow the pos order lines be copied to the sale order.",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Point of sale",
    "website": "https://github.com/nuobit",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "maintainers": ["eantones"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pos_restaurant",
        "wv_pos_create_so",
    ],
}
