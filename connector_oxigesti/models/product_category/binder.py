# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ProductCategoryBinder(Component):
    _name = "oxigesti.product.category.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.product.category"

    def _get_external_id(self, relation, extra_vals=None):
        adapter = self.component(
            usage="backend.adapter", model_name="oxigesti.product.category"
        )
        external_ids = adapter.search([("IdCategoriaOdoo", "=", relation.id)])
        if not external_ids:
            return None
        if len(external_ids) > 1:
            raise ValidationError(
                _("More than one Category with ID '%i' on the backend" % (relation.id,))
            )

        return external_ids[0]
