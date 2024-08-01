# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Move Service Report",
    "summary": "Module to attach xlsx reports along with the creation of "
    "invoices with all detailed lines.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Sales/Accounting",
    "license": "AGPL-3",
    "depends": ["account_move_service", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/reports.xml",
        "views/res_partner_views.xml",
        "views/sale_order_report_xlsx_mapping_config_views.xml",
        "wizard/sale_make_invoice_advance_views.xml",
    ],
}
