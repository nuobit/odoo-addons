# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class WooCommerceWPMLSaleOrderLineImportMapper(Component):
    _name = "woocommerce.wpml.sale.order.line.import.mapper"
    _inherit = "woocommerce.wpml.import.mapper"

    _apply_on = "woocommerce.wpml.sale.order.line"

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def woocommerce_line_id(self, record):
        binder = self.binder_for()
        external_id = binder.dict2id(record, in_field=False)
        return binder.id2dict(external_id, in_field=True)

    @mapping
    def price_unit(self, record):
        return {"price_unit": (float(record["subtotal"])) / record["quantity"]}

    @mapping
    def price_total(self, record):
        return {"price_total": float(record["subtotal"])}

    @mapping
    def price_tax(self, record):
        return {"price_tax": float(record["total_tax"])}

    @mapping
    def price_subtotal(self, record):
        return {"price_subtotal": float(record["total"])}

    @mapping
    def product_id(self, record):
        if record["is_shipping"]:
            shipping_product = self.backend_record.shipping_product_id
            if not shipping_product:
                raise ValidationError(
                    _("Shipping product not found, please define it on Backend")
                )
            return {"product_id": shipping_product.id}
        if record.get("variation_id"):
            external_id = [record["product_id"], record["variation_id"]]
            binder = self.binder_for("woocommerce.wpml.product.product")
            product_odoo = binder.to_internal(external_id, unwrap=True)
        else:
            if not record.get("product_id"):
                raise ValidationError(
                    _(
                        "Product not found in order line. "
                        "Probably this product has been deleted in WooCommerce."
                    )
                )
            external_id = [record["product_id"]]
            binder = self.binder_for("woocommerce.wpml.product.template")
            product_tmpl = binder.to_internal(external_id, unwrap=True)
            product_odoo = product_tmpl.product_variant_id
        assert product_odoo, (
            "product_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"product_id": product_odoo.id}

    @mapping
    def tax_id(self, record):
        if record.get("taxes"):
            taxes = []
            for tax in record.get("taxes"):
                if tax["total"]:
                    tax_map = self.backend_record.tax_map_ids.filtered(
                        lambda x: tax["id"] == int(x.woocommerce_tax_rate_id)
                    )
                    if not tax_map:
                        raise ValidationError(
                            _("Tax rate %s not found in backend mapping.") % tax["id"]
                        )
                    else:
                        taxes.append(tax_map.account_tax.id)
            if taxes:
                return {"tax_id": [(6, 0, taxes)]}

    @mapping
    def quantity(self, record):
        return {"product_uom_qty": record["quantity"]}

    @mapping
    def order(self, record):
        external_id = [record["order_id"]]
        binder = self.binder_for("woocommerce.wpml.sale.order")
        order = binder.to_internal(external_id, unwrap=True)
        return {"order_id": order}

    @mapping
    def woocommerce_discount(self, record):
        return {
            "woocommerce_discount": record["discount"],
            "discount": record["discount"],
        }
