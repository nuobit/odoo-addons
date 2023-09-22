# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Service invoice report",
    "summary": """Service invoice report""",
    "version": "14.0.1.1.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["sale_order_service", "account_payment_partner"],
    "data": [
        "data/data.xml",
        "report/report.xml",
        "views/res_config_settings_views.xml",
        "views/report_invoice_service.xml",
        "views/report_invoice_delivery.xml",
        "views/account_invoice_views.xml",
    ],
    "installable": True,
}
