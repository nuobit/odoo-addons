# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    woocommerce_tax_class_ids = fields.One2many(
        comodel_name="woocommerce.backend.tax.class",
        inverse_name="account_tax_id",
        string="WooCommerce Tax Classes",
    )
