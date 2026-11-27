# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Connector WooCommerce Invoice Batches",
    "summary": "The invoice batch sending method of the customers the "
    "WooCommerce import creates",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "account_invoice_batches",
        "connector_woocommerce",
    ],
    "data": [
        "views/woocommerce_backend_view.xml",
    ],
    "auto_install": True,
}
