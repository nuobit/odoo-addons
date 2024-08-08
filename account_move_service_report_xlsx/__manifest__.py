# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Move Service Report XLSX",
    "summary": "This module generates a spreadsheet of sales services "
    "from the invoice.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Sales/Accounting",
    "license": "AGPL-3",
    "depends": ["account_move_service", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_partner_service_report_config_security.xml",
        "views/reports.xml",
        "views/res_partner_views.xml",
        "views/res_partner_service_report_config_views.xml",
        "views/account_move_views.xml",
        "views/account_menuitem.xml",
    ],
}
