# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models

from ..binding.binding import WoocommerceWPMLBindingMixin


class WooCommerceProductProduct(models.Model):
    _name = "woocommerce.product.product"
    _inherit = [
        "woocommerce.product.product",
        "woocommerce.wpml.binding.mixin",
    ]

    _sql_constraints = WoocommerceWPMLBindingMixin._sql_constraints

    # TODO: This function should be an overwrite of the original one,
    #  it should be refactored to avoid code duplication
    #  doing a hook to set a context variable with lang
    #  TODO: The optimization needs to be done at the language level,
    #   just as we do in the upper module connector_woocommerce
    # def resync_export(self):
    #     super().resync_export()
    #     if not self.env.context.get("resync_product_template", False):
    #         for rec in self:
    #             rec.product_tmpl_id.woocommerce_bind_ids.filtered(
    #                 lambda x: x.backend_id == rec.backend_id
    #                 and x.woocommerce_lang == rec.woocommerce_lang
    #             ).with_context(resync_product_product=True).resync_export()
