# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Asset Review",
    "summary": "Module to allow certain users "
    "to modify the protected asset fields of the invoices.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": [
        "account_asset_invoice_line_link",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/account_asset_views.xml",
        "wizard/account_move_asset_review_wizard.xml",
    ],
}
