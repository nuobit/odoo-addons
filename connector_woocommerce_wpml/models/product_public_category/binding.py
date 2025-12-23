# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..binding.binding import WoocommerceWPMLBindingMixin


class WooCommerceProductPublicCategory(models.Model):
    _name = "woocommerce.product.public.category"
    _inherit = [
        "woocommerce.product.public.category",
        "woocommerce.wpml.binding.mixin",
    ]

    # TODO: add this to the mixin
    woocommerce_master_lang = fields.Boolean(
        string="WooCommerce Master Language",
        readonly=True,
        required=True,
        default=False,
    )

    _sql_constraints = WoocommerceWPMLBindingMixin._sql_constraints

    @api.constrains("woocommerce_master_lang", "backend_id", "odoo_id")
    def _check_woocommerce_master_lang(self):
        for rec in self:
            master_bindings = rec.odoo_id.woocommerce_bind_ids.filtered(
                lambda x: x.backend_id == rec.backend_id and x.woocommerce_master_lang
            )
            if len(master_bindings) != 1:
                raise ValidationError(
                    _(
                        "It should always be one and exactly one binding with"
                        " master language enabled"
                    )
                )
