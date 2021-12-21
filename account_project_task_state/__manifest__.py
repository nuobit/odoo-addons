# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Project Task State",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module links the invoice and payment state "
    "to related task state.",
    "depends": [
        "project_task_metatype",
        "sale",
        "account",
    ],
    "data": [
        "data/account_project_task_state_cron.xml",
    ],
    "installable": True,
}
