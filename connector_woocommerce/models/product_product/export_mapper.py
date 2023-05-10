# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductProductExportMapper(Component):
    _name = "woocommerce.product.product.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.product"

    @mapping
    def price(self, record):
        # TODO: Revisar esto, el sale price no se exporta si es
        #  igual que el regular. si el regular no esta informado, no se exporta.
        #      El regular price deberia ser menor que el regular,
        #      si no tampoco se exporta.
        return {
            "regular_price": str(record.lst_price),
            "sale_price": str(record.lst_price),
        }

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        return {"sku": record.default_code or None}

    @changed_by("active")
    @mapping
    def status(self, record):
        if record.active:
            return {"status": "publish"}
        else:
            return {"status": "pending"}

    @mapping
    def stock(self, record):
        return {
            "manage_stock": True,
            "stock_quantity": record.qty_available,
            "stock_status": "instock" if record.qty_available > 0 else "outofstock",
        }

    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.template")
        values = binder.get_external_dict_ids(record.product_tmpl_id)
        return {"parent_id": values["id"]}

    @mapping
    def image(self, record):
        if record.image_1920 != record.product_tmpl_id.image_1920:
            if self.collection.wordpress_backend_id:
                with self.collection.wordpress_backend_id.work_on(
                    "wordpress.ir.attachment"
                ) as work:
                    exporter = work.component(self._usage)
                    binder = exporter.binder_for("wordpress.ir.attachment")
                    image = self.env["ir.attachment"].search(
                        [
                            ("res_model", "=", record._name),
                            ("res_id", "=", record.id),
                            ("res_field", "=", "image_variant_1920"),
                        ]
                    )
                    values = binder.get_external_dict_ids(image)
                    # values = binder.get_external_dict_ids(image, check_external_id=False)
                    # external_id = exporter.binder_for(
                    #     "wordpress.ir.attachment"
                    # ).to_external(image, wrap=False)
                    return {
                        "image": {
                            "id": values["id"],
                        }
                    }

    @mapping
    def attributes(self, record):
        binder = self.binder_for("woocommerce.product.attribute")
        attr_list = []
        for value in record.product_template_attribute_value_ids:
            values = binder.get_external_dict_ids(value.attribute_id)
            attr_list.append(
                {
                    "id": values["id"],
                    "option": value.name,
                }
            )
        return {"attributes": attr_list}
