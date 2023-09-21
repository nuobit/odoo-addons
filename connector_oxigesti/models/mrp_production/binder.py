# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionBinder(Component):
    _name = "oxigesti.mrp.production.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.mrp.production"

    # def _get_external_id(self, binding):
    #     if not self._is_binding(binding):
    #         raise Exception("The source object %s must be a binding" % binding._name)
    #
    #     external_id = None
    #     if binding.odoo_id.product_id.default_code:
    #         external_id = [binding.odoo_id.product_id.default_code]
    #
    #     return external_id
