# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Invoices Batches Mail Attach Existing Attachment",
    "summary": "Glue module for account invoices batches and account mail attach "
    "existing attachment",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["account_invoice_batches", "account_mail_attach_existing_attachment"],
    "data": [
        "views/res_partner_view.xml",
        "views/account_move_view.xml",
        "wizard/account_invoice_batch_process.xml",
    ],
    "auto_install": True,
}
