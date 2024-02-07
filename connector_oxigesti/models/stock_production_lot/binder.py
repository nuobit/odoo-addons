# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class StockProductionLotBinder(Component):
    _name = "oxigesti.stock.production.lot.binder"
    _inherit = "oxigesti.binder"

    _apply_on = "oxigesti.stock.production.lot"

    def _get_external_id(self, relation, extra_vals=None):
        product_binder = self.binder_for("oxigesti.product.product")
        product_external_id = product_binder.to_external(relation.product_id, wrap=True)

        external_id = None
        if product_external_id:
            product_adapter = self.component(
                usage="backend.adapter", model_name="oxigesti.product.product"
            )
            codigo_articulo = product_adapter.id2dict(product_external_id)[
                "CodigoArticulo"
            ]
            external_id = [codigo_articulo, relation.name]

        return external_id
