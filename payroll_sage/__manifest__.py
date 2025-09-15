# Copyright 2021 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sage Payroll",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Human Resources",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "account",
        "hr",
    ],
    "data": [
        "security/payroll_sage.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/labour_agreement_view.xml",
        "views/payslip_view.xml",
        "views/wage_tag_view.xml",
        "views/payslip_process_view.xml",
        "views/menu.xml",
    ],
}
