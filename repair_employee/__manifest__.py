# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Repair Employee",
    "summary": "Add employee field and assigned date to repair orders",
    "version": "17.0.1.0.0",
    "category": "Repairs",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "repair",
        "hr",
    ],
    "data": [
        "views/repair_views.xml",
    ],
    "installable": True,
    "application": False,
}
