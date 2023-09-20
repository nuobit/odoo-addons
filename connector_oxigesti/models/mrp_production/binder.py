# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionBinder(Component):
    _name = "oxigesti.mrp.production.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.mrp.production"

    def _get_external_id(self, binding):
        if not self._is_binding(binding):
            raise Exception("The source object %s must be a binding" % binding._name)

        product_binder = self.binder_for("oxigesti.mrp.production")
        product_external_id = product_binder.to_external(
            binding.odoo_id.product_id, wrap=True
        )

        external_id = None
        if product_external_id:
            product_adapter = self.component(
                usage="backend.adapter", model_name="oxigesti.mrp.production"
            )
            codigo_articulo = product_adapter.id2dict(product_external_id)[
                "CodigoOrdenProduccion"
            ]
            external_id = [codigo_articulo, binding.name]

        return external_id
