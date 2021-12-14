# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
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

        return {"CodigoArticulo": external_id[0]}
