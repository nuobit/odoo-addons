# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.public.category",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )

    def _dict_binding_data(self, binding):
        with binding.backend_id.work_on(binding._name) as work:
            binder = work.component(usage="binder")
            external_id = binder.to_external(binding)
            return {
                "backend": binding.backend_id,
                "binding_name": binding._name,
                "external_id": external_id,
            }

    def unlink(self):
        to_remove = []
        categories_with_bindings = self.filtered(lambda x: x.woocommerce_bind_ids)
        if len(categories_with_bindings) > 1:
            raise ValidationError(
                _(
                    "Not supported: It's not possible delete more than one "
                    "category with WooCommerce bindings at the same time"
                )
            )
        children_with_bindings = categories_with_bindings.search(
            [("parent_id", "=", self.ids)]
        ).filtered(lambda x: x.woocommerce_bind_ids)
        if children_with_bindings:
            raise ValidationError(
                _(
                    "Not supported: It's not possible delete a category '%s' with "
                    "WooCommerce bindings if it has children with WooCommerce "
                    "bindings. Delete first the children %s"
                )
                % (categories_with_bindings.name, children_with_bindings.mapped("name"))
            )

        for record in self:
            for binding in record.woocommerce_bind_ids:
                to_remove.append(self._dict_binding_data(binding))
        result = super().unlink()
        for bindings_data in to_remove:
            self._event("on_record_post_unlink").notify(bindings_data)
        return result
