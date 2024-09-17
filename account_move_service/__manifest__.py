# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Move Service",
    "summary": "Module to allow grouping service billing in account moves",
    "version": "14.0.1.0.1",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Sales/Accounting",
    "license": "AGPL-3",
    "depends": ["sale_order_service"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/report_invoice_document.xml",
    ],
}
