# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionDelayedBatchExporter(Component):
    """Export the Oxigesti Productions.

    For every production in the list, a delayed job is created.
    """

    _name = "oxigesti.mrp.production.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.mrp.production"


class MrpProductionDirectBatchExporter(Component):
    """Export the Oxigesti Productions.

    For every production in the list, execute inmediately.
    """

    _name = "oxigesti.mrp.production.direct.batch.exporter"
    _inherit = "oxigesti.direct.batch.exporter"

    _apply_on = "oxigesti.mrp.production"


class MrpProductionExporter(Component):
    _name = "oxigesti.mrp.production.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.mrp.production"

    def _export_dependencies(self):
        binder = self.binder_for("oxigesti.mrp.production")
        mrp_production = binder.unwrap_binding(self.binding)
        components = mrp_production._get_valid_components()
        items_dict = {
            "oxigesti.stock.production.lot": mrp_production.lot_producing_id
            | components.move_line_ids.lot_id,
            "oxigesti.product.product": mrp_production.product_id
            | components.product_id,
        }
        for binder_name, items in items_dict.items():
            binder = self.binder_for(binder_name)
            for item in items:
                if not binder.to_external(item, wrap=True):
                    exporter = self.component(
                        usage="record.exporter", model_name=binder.model._name
                    )
                    exporter.run(item)
