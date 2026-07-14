# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sage-Odoo connector",
    "version": "18.0.1.0.1",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "connector",
        "hr",
        "payroll_sage",
    ],
    "external_dependencies": {
        "python": [
            "pymssql<=2.2.5 ; python_version <= '3.10'",
            "pymssql<=2.2.8 ; python_version < '3.12'",
            "pymssql<=2.3.7 ; python_version >= '3.12'",
        ],
    },
    "data": [
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/sage_backend_views.xml",
        "views/hr_employee_views.xml",
        "views/res_partner_views.xml",
        "views/payroll_sage_labour_agreement_views.xml",
        "views/payroll_sage_payslip_line_views.xml",
        "views/payroll_sage_payslip_check_views.xml",
        "views/payroll_sage_payslip_views.xml",
        "views/connector_sage_menus.xml",
        "security/connector_sage.xml",
        "security/ir.model.access.csv",
    ],
}
