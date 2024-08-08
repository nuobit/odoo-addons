# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WooCommerceProductTemplate(models.Model):
    _inherit = "woocommerce.product.template"

    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, woocommerce_lang, woocommerce_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    # TODO: This function should be an overwrite of the original one,
    #  it should be refactored to avoid code duplication
    #  doing a hook to set a context variable with lang
    def resync_export(self):
        super().resync_export()
        if not self.env.context.get("resync_product_product", False):
            for rec in self:
                rec.product_variant_ids.woocommerce_bind_ids.filtered(
                    lambda x: x.backend_id == self.backend_id
                ).with_context(
                    resync_product_template=True, lang=rec._context.get("lang")
                ).resync_export()
