# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Project Task State",
    "version": "12.0.1.0.2",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/OCA/pms",
    "summary": "This module links the invoice and payment state "
    "to related task state.",
    "depends": [
        "project",
        "sale",
        "account",
    ],
    "data": [
        "data/account_project_task_state_cron.xml",
        "views/project_task_views.xml",
        "views/project_task_type_views.xml",
    ],
    "installable": True,
}
