# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


class OxigestiSpmsProductProductImporterMapper(Component):
    _name = "oxigesti.spms.product.product.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.product.product"
    _usage = "import.mapper"

    # direct = [
    #     ("Codigo", "default_code"),
    #     ("Nome", "name"),
    # ]

    @only_create
    @mapping
    def type(self, record):
        """Set the product type to 'service' for SPMS products."""
        return {"type": "service"}

    @only_create
    @mapping
    def default_code(self, record):
        return {"default_code": record["Codigo"]}

    @only_create
    @mapping
    def name(self, record):
        return {"name": record["Nome"]}

    @changed_by("spms_lot_id")
    @mapping
    def spms_lot_id(self, record):
        binder = self.binder_for("oxigesti.spms.spms.lot")
        external_id = record["Lote"]
        lot = binder.to_internal(external_id, unwrap=True)
        assert lot, (
            "spms_lot_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"spms_lot_id": lot.id}
