# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Partner default journal",
    "summary": "Set Default Sale and Purchase Journal on partner.",
    "version": "12.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "account",
        "purchase",
        "sale",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
