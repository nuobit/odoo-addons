# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Invoice batches Accrual Entry",
    "summary": "Glue module to avoid create the accrual entry "
    "inside the same invoice batch as its origin",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account_invoice_batches", "account_move_accrual_entry"],
    "maintainers": ["eantones"],
    "auto_install": True,
}
