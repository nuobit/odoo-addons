# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Purchase order new line uom",
    "summary": "This module allows to edit the uom on new purchase "
    "order lines that don't have any invoice or stock move linked.",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "category": "Purchases",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "installable": True,
}
