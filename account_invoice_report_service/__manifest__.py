# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Service invoice report",
    "summary": """Service invoice report""",
    "version": "17.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/NuoBiT/odoo-addons",
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
    "assets": {
        "web.report_assets_common": [
            "account_invoice_report_service/static/src/scss/report_invoice_service_styles.scss",
            "account_invoice_report_service/static/src/scss/report_invoice_delivery_styles.scss",
        ],
    },
}
