# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SaleOrderLineImportMapper(Component):
    _name = "lengow.sale.order.line.import.mapper"
    _inherit = "lengow.import.mapper"

    _apply_on = "lengow.sale.order.line"

    @mapping
    def lengow_line_id(self, record):
        binder = self.binder_for()
        external_id = binder.dict2id(record, in_field=False)
        return binder.id2dict(external_id, in_field=True)

    @mapping
    def price_unit(self, record):
        if record["quantity"]:
            return {"price_unit": (float(record["amount"])) / record["quantity"]}
        binding = self.options.get("binding")
        if not binding:
            return {"price_unit": (float(record["amount"]))}

    @mapping
    def product(self, record):
        if record["is_shipping"]:
            shipping_product = self.backend_record.shipping_product_id
            if not shipping_product:
                raise ValidationError(
                    _("Shipping product not found, please define it on Backend")
                )
            return {"product_id": shipping_product.id}
        external_id = record["sku"] or record["marketplace_product_id"]
        if not external_id:

            raise ValidationError(
                _("Product SKU not found. This SKU should be defined on Lengow")
            )
        binder = self.binder_for("lengow.product.product")
        product_odoo = binder.to_internal(external_id, unwrap=True)
        assert product_odoo, (
            "product_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"product_id": product_odoo.id}

    @mapping
    def quantity(self, record):
        if not record["quantity"] == 0:
            return {"product_uom_qty": record["quantity"]}
        else:
            binding = self.options.get("binding")
            if not binding:
                return {"product_uom_qty": record["quantity"]}
