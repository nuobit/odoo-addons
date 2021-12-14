# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductBinder(Component):
    """Bind records and give odoo/oxigesti ids correspondence

    Binding models are models called ``oxigesti.{normal_model}``,
    like ``oxigesti.res.partner`` or ``oxigesti.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Oxigesti ID, the ID of the Oxigesti Backend and the additional
    fields belonging to the Oxigesti instance.
    """

    _name = "oxigesti.product.product.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.product.product"

    def _get_external_id(self, binding):
        if not self._is_binding(binding):
            raise Exception("The source object %s must be a binding" % binding._name)

        external_id = None
        if binding.odoo_id.default_code:
            external_id = [binding.odoo_id.default_code]

        return external_id
