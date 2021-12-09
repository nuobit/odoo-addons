# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductDelayedBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.product.product.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.product.product"


class ProductProductDirectBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, execute inmediately.
    """

    _name = "oxigesti.product.product.direct.batch.exporter"
    _inherit = "oxigesti.direct.batch.exporter"

    _apply_on = "oxigesti.product.product"


class ProductProductExporter(Component):
    _name = "oxigesti.product.product.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.product.product"

    def _export_dependencies(self):
        # category
        binder = self.binder_for("oxigesti.product.category")
        relation = self.binding.with_context(active_test=False).categ_id
        if not binder.to_external(relation, wrap=True):
            exporter = self.component(
                usage="record.exporter", model_name=binder.model._name
            )
            exporter.run(relation)
