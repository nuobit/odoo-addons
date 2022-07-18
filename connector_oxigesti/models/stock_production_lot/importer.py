# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class StockProductionLotDelayedBatchImporter(Component):
    """Import the Oxigesti Stock Production Lots.

    For every stock production lot in the list, a delayed job is created.
    """

    _name = "oxigesti.stock.production.lot.delayed.batch.importer"
    _inherit = "oxigesti.delayed.batch.importer"

    _apply_on = "oxigesti.stock.production.lot"


class StockProductionLotDirectBatchImporter(Component):
    """Import the Oxigesti Stock Production Lots.

    For every stock production lot in the list, import it directly.
    """

    _name = "oxigesti.stock.production.lot.direct.batch.importer"
    _inherit = "oxigesti.direct.batch.importer"

    _apply_on = "oxigesti.stock.production.lot"


class StockProductionLotImporter(Component):
    _name = "oxigesti.stock.production.lot.importer"
    _inherit = "oxigesti.importer"

    _apply_on = "oxigesti.stock.production.lot"

    def _import_dependencies(self):
        # Product
        exporter = self.component(
            usage="direct.batch.exporter", model_name="oxigesti.product.product"
        )
        exporter.run(
            domain=[
                ("company_id", "=", self.backend_record.company_id.id),
                ("default_code", "=", self.external_data["CodigoArticulo"]),
            ]
        )

    def _must_skip(self, binding):
        if not binding:
            return False
        external_id = self.binder.to_external(binding)
        if external_id:
            if not self.external_data["write_date"]:
                return True
            return self.external_data["write_date"] <= binding.oxigesti_write_date
        return False

    def _create(self, values):
        raise ValidationError(_("It's not allowed to create a new lots from Oxigesti."))
