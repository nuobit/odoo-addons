# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionDelayedBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.mrp.production.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.mrp.production"


class MrpProductionDirectBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, execute inmediately.
    """

    _name = "oxigesti.mrp.production.direct.batch.exporter"
    _inherit = "oxigesti.direct.batch.exporter"

    _apply_on = "oxigesti.mrp.production"


class MrpProductionExporter(Component):
    _name = "oxigesti.mrp.production.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.mrp.production"

    def _export_dependencies(self):
        binder = self.binder_for("oxigesti.product.product")
        relation = self.binding.with_context(active_test=False).product_id
        if not binder.to_external(self.binding.product_id, wrap=True):
            exporter = self.component(
                usage="record.exporter", model_name=binder.model._name
            )
            exporter.run(relation)
