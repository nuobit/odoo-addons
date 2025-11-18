# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models

from ..binding.binding import WoocommerceWPMLBindingMixin


class WooCommerceProductAttributeValue(models.Model):
    _name = "woocommerce.product.attribute.value"
    _inherit = [
        "woocommerce.product.attribute.value",
        "woocommerce.wpml.binding.mixin",
    ]

    _sql_constraints = WoocommerceWPMLBindingMixin._sql_constraints
