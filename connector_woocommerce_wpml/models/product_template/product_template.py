# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    woocommerce_wpml_bind_ids = fields.One2many(
        comodel_name="woocommerce.wpml.product.template",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )

    # def unlink(self):
    #     categories_with_bindings = self.filtered(lambda x: x.woocommerce_bind_ids)
    #     if len(categories_with_bindings) > 1:
    #         raise ValidationError(
    #             _(
    #                 "Not supported: It's not possible delete more than one "
    #                 "category with WooCommerce bindings at the same time"
    #             )
    #         )
    #     children_with_bindings = categories_with_bindings.search(
    #         [("parent_id", "in", self.ids)]
    #     ).filtered(lambda x: x.woocommerce_bind_ids)
    #     if children_with_bindings:
    #         raise ValidationError(
    #             _(
    #                 "Not supported: It's not possible delete a category '%s' with "
    #                 "WooCommerce bindings if it has children with WooCommerce "
    #                 "bindings. Delete first the children %s"
    #             )
    #             % (categories_with_bindings.name, children_with_bindings.mapped("name"))
    #         )
    #     return super(
    #         ProductPublicCategory,
    #         self.with_context(binding_field="woocommerce_bind_ids"),
    #     ).unlink()
