# Copyright NuoBiT Solution - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Invoice batches Accrual Entry",
    "summary": "Glue module to avoid create the accrual entry "
    "inside the same invoice batch as its origin",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account_invoice_batches", "account_move_accrual_entry"],
    "maintainers": ["eantones"],
}
