# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale order exclude invoicing",
    "summary": "Exclude orders from being invoiced.",
    "version": "11.0.1.2.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "sale_order_invoicing_grouping_criteria",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
