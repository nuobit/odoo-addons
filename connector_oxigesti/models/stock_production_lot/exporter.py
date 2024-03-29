# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class StockProductionLotBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.stock.production.lot.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.stock.production.lot"


class StockProductionLotDirectBatchExporter(Component):
    """Export the Oxigesti Lot.

    For every Lot in the list, execute inmediately.
    """

    _name = "oxigesti.stock.production.lot.direct.batch.exporter"
    _inherit = "oxigesti.direct.batch.exporter"

    _apply_on = "oxigesti.stock.production.lot"


class StockProductionLotExporter(Component):
    _name = "oxigesti.stock.production.lot.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.stock.production.lot"

    def _must_skip(self, binding):
        if not binding:
            return False
        external_id = self.binder.to_external(binding)
        if external_id:
            external_record = self.backend_adapter.read(external_id)
            if external_record:
                return (
                    bool(external_record["write_date"])
                    and binding.oxigesti_write_date <= external_record["write_date"]
                )
        return False

    def _export_dependencies(self):
        binder = self.binder_for("oxigesti.product.product")
        relation = self.binding.with_context(active_test=False).product_id
        if not binder.to_external(self.binding.product_id, wrap=True):
            exporter = self.component(
                usage="record.exporter", model_name=binder.model._name
            )
            exporter.run(relation)
