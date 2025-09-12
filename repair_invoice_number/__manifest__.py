# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Repair Invoice Number",
    "summary": "Add repair order number to invoice",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account", "repair"],
    "data": [
        "views/account_move_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}