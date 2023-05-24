# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderLineImportMapper(Component):
    _name = "woocommerce.sale.order.line.import.mapper"
    _inherit = "woocommerce.import.mapper"

    _apply_on = "woocommerce.sale.order.line"

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
    def product(self, record):
        if record.get("variation_id"):
            external_id = [record["product_id"], record["variation_id"]]
            binder = self.binder_for("woocommerce.product.product")
            product_odoo = binder.to_internal(external_id, unwrap=True)
        #     TODO: si el producto es simple, deberiamos devolver
        #      directamente el product_product de esa template,
        #      haciendo el to_internal del product_template en lugar del product.product
        #       debugar para ver si es correcto
        else:
            external_id = [record["product_id"]]
            binder = self.binder_for("woocommerce.product.template")
            product_tmpl = binder.to_internal(external_id, unwrap=True)
            product_odoo = product_tmpl.product_variant_id
        assert product_odoo, (
            "product_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"product_id": product_odoo.id}

    @mapping
    def quantity(self, record):
        return {"product_uom_qty": record["quantity"]}
        # if not record["quantity"] == 0:
        #     return {"product_uom_qty": record["quantity"]}
        # else:
        #     binding = self.options.get("binding")
        #     if not binding:
        #         return {"product_uom_qty": record["quantity"]}
