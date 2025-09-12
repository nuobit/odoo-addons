# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Move Repair Order",
    "summary": "Add repair order number to invoice",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "account",
        "repair",
    ],
    "data": [
        "views/account_move_views.xml",
        "views/repair_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
