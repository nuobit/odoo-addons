# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBit Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale line product variant description by partner",
    "summary": "This module replaces the default product description "
    "on sale order lines with the product’s sales description. "
    "As a result, no product description will appear on a sale "
    "order line unless the product has a customer-specific sales "
    "description.",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale_order_line_variant_description_extension",
        "sale_line_partner_description",
    ],
}
