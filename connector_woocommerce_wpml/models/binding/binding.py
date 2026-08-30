# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WoocommerceWPMLBindingMixin(models.AbstractModel):
    _name = "woocommerce.wpml.binding.mixin"
    _description = "WooCommerce WPML Binding Mixin"

    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
    )

    # overwrite the constraint of the parent with the lang field
    # the names should be this one to be sure they overwrite the parents
    _sql_constraints = [
        (
            "internal_uniq",
            "unique(backend_id, odoo_id, woocommerce_lang)",
            "A binding already exists with the same language, "
            "hence with the same Internal (Odoo) ID.",
        ),
    ]
