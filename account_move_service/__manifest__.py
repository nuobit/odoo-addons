# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Move Service",
    "summary": "Module to allow grouping service billing in account moves",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "category": "Sales/Accounting",
    "license": "AGPL-3",
    "depends": ["sale_order_service"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "report/report_invoice_document.xml",
    ],
}
