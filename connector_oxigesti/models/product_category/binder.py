# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ProductCategoryBinder(Component):
    _name = "oxigesti.product.category.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.product.category"

    def _get_external_id(self, binding):
        if not self._is_binding(binding):
            raise Exception("The source object %s must be a binding" % binding._name)

        adapter = self.component(
            usage="backend.adapter", model_name="oxigesti.product.category"
        )
        external_ids = adapter.search([("IdCategoriaOdoo", "=", binding.odoo_id.id)])
        if not external_ids:
            return None
        if len(external_ids) > 1:
            raise ValidationError(
                "More than one Category with ID '%i' on the backend"
                % (binding.odoo_id.id,)
            )

        return external_ids[0]
