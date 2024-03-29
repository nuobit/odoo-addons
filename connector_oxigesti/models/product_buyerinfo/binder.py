# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductBuyerinfoBinder(Component):
    _name = "oxigesti.product.buyerinfo.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.product.buyerinfo"

    def _get_external_id(self, binding):
        if not self._is_binding(binding):
            raise Exception("The source object %s must be a binding" % binding._name)

        partner_adapter = self.component(
            usage="backend.adapter", model_name="oxigesti.res.partner"
        )
        partner_binder = self.binder_for("oxigesti.res.partner")
        partner_external_id = partner_binder.to_external(
            binding.odoo_id.partner_id, wrap=True
        )

        external_id = None
        if partner_external_id:
            codigo_articulo = binding.odoo_id.product_id.default_code
            codigo_mutua = partner_adapter.id2dict(partner_external_id)["Codigo_Mutua"]
            if codigo_articulo and codigo_mutua:
                external_id = [codigo_articulo, codigo_mutua]

        return external_id
