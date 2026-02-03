# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..binding.binding import WoocommerceWPMLBindingMixin


class WooCommerceProductProduct(models.Model):
    _name = "woocommerce.product.product"
    _inherit = [
        "woocommerce.product.product",
        "woocommerce.wpml.binding.mixin",
    ]
    _order = (
        "backend_id, product_tmpl_id, odoo_id, woocommerce_master_lang desc, "
        " woocommerce_lang, woocommerce_idparent,"
        "woocommerce_idproduct"
    )

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

    # def unlink(self):
    #     to_remove, to_remove_variants = self.env[self._name],
    #     self.env["woocommerce.product.product"]
    #     for rec in self:
    #         to_remove |= rec.odoo_id.woocommerce_bind_ids.filtered(
    #             lambda x: x.backend_id == rec.backend_id #and x != rec
    #         )
    #         to_remove_variants |= rec.odoo_id.with_context(active_test=False)
    #         .product_variant_ids.woocommerce_bind_ids.filtered(
    #             lambda x: x.backend_id == rec.backend_id
    #     )
    #     to_remove_variants.with_context().unlink()
    #     return super(WooCommerceProductTemplate, to_remove).unlink()
