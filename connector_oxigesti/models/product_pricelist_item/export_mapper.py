# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductPricelistItemExportMapper(Component):
    _name = "oxigesti.product.pricelist.item.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.product.pricelist.item"

    direct = [
        ("fixed_price", "Importe"),
    ]

    @only_create
    @mapping
    def CodigoArticulo(self, record):
        product_id = record.with_context(
            active_test=False
        ).product_tmpl_id.product_variant_id
        binder = self.binder_for("oxigesti.product.product")
        external_id = binder.to_external(product_id, wrap=True)
        assert external_id, (
            f"{record}: There's no bond between Odoo product and "
            "Oxigesti product, so the Oxigesti ID cannot be obtained. "
            "At this stage, the Oxigesti product should have been linked via "
            "ProductProduct._export_dependencies. "
            f"If not, then this product {product_id.display_name} "
            f"({product_id.default_code}) with code '%s' "
            "does not exist in Oxigesti."
        )

        return {"CodigoArticulo": external_id[0]}

    @only_create
    @mapping
    def Codigo_Mutua(self, record):
        partner_id = record.with_context(active_test=False).odoo_partner_id
        binder = self.binder_for("oxigesti.res.partner")
        external_id = binder.to_external(partner_id, wrap=True)
        if not external_id:
            display_name_l = []
            if partner_id.ref:
                display_name_l.append(f"[{partner_id.ref}]")
            if partner_id.name:
                display_name_l.append(partner_id.name)
            display_name = " ".join(display_name_l)
            raise AssertionError(
                f"{record}: There's no bond between Odoo partner and "
                f"Oxigesti partner so the Oxigesti ID cannot be obtained. "
                f"At this stage, the Oxigesti partner should have been linked via "
                f"ResPartner._import_dependencies. "
                f"If not, then this partner {partner_id} "
                f"({display_name}) with code '{partner_id.ref}' "
                f"does not exist in Oxigesti."
            )

        return {"Codigo_Mutua": external_id[0]}

    @mapping
    def Deprecated(self, record):
        return {"Deprecated": 0}
