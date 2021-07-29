# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class StockProductionLotBatchExporter(Component):
    """ Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """
    _name = 'oxigesti.stock.production.lot.delayed.batch.exporter'
    _inherit = 'oxigesti.delayed.batch.exporter'

    _apply_on = 'oxigesti.stock.production.lot'


class StockProductionLotExporter(Component):
    _name = 'oxigesti.stock.production.lot.exporter'
    _inherit = 'oxigesti.exporter'

    _apply_on = 'oxigesti.stock.production.lot'

    def _export_dependencies(self):
        binder = self.binder_for('oxigesti.product.product')
        relation = self.binding.with_context(active_test=False).product_id
        if not binder.to_external(self.binding.product_id, wrap=True):
            exporter = self.component(usage='record.exporter',
                                      model_name=binder.model._name)
            exporter.run(relation)
