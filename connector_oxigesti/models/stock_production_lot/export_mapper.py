# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class StockProductionLotExportMapper(Component):
    _name = "oxigesti.stock.production.lot.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.stock.production.lot"

    direct = [
        ("name", "Lote"),
    ]

    @mapping
    def CodigoArticulo(self, record):
        product_id = record.product_id
        binder = self.binder_for("oxigesti.product.product")
        external_id = binder.to_external(product_id, wrap=True)
        assert external_id, (
            f"{record}: There's no bond between Odoo product and "
            "Oxigesti product, so the Oxigesti ID cannot be obtained. "
            "At this stage, the Oxigesti product should have been linked via "
            "ProductProduct._export_dependencies. "
            f"If not, then this product {product_id} "
            f"({product_id.display_name}) with code "
            f"'{product_id.default_code}' does not exist in Oxigesti."
        )
        adapter = self.component(usage="backend.adapter")
        return adapter.id2dict(external_id)

    @mapping
    def nos(self, record):
        if record.nos_enabled:
            nos, unknown = record.nos or None, record.nos_unknown
        else:
            nos, unknown = None, None
        return {"nos": nos, "nos_unknown": unknown}

    @mapping
    def dn(self, record):
        if record.dn_enabled:
            dn, unknown = record.dn or None, record.dn_unknown
        else:
            dn, unknown = None, None
        return {"dn": dn, "dn_unknown": unknown}

    @mapping
    def write_date(self, record):
        return {"write_date": record.oxigesti_write_date}
