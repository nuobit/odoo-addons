# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
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
            "%s: There's no bond between Odoo product and "
            "Oxigesti product, so the Oxigesti ID cannot be obtained. "
            "At this stage, the Oxigesti product should have been linked via "
            "ProductProduct._export_dependencies. "
            "If not, then this product %s (%s) with code '%s' "
            "does not exist in Oxigesti."
            % (record, product_id, product_id.display_name, product_id.default_code)
        )
        adapter = self.component(usage="backend.adapter")
        return adapter.id2dict(external_id)

    @mapping
    def nos(self, record):
        return {"nos": record.nos or None, "nos_unknown": record.nos_unknown}

    @mapping
    def dn(self, record):
        return {"dn": record.dn or None, "dn_unknown": record.dn_unknown}

    @mapping
    def manufacturer(self, record):
        return {"manufacturer": record.manufacturer.name or None}

    @mapping
    def weight(self, record):
        return {"weight": record.weight or None}

    @mapping
    def manufacture_date(self, record):
        return {"manufacture_date": record.manufacture_date or None}

    @mapping
    def retesting_date(self, record):
        return {"retesting_date": record.retesting_date or None}

    @mapping
    def next_retesting_date(self, record):
        return {"next_retesting_date": record.next_retesting_date or None}

    @mapping
    def removal_date(self, record):
        return {"removal_date": record.removal_date or None}

    @mapping
    def write_date(self, record):
        return {"write_date": record.oxigesti_write_date}
