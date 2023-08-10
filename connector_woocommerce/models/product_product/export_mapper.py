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
        # On WooCommerce regular price is the usually price.
        # sales price is the price with discount.
        # On odoo we don't have this functionality per product
        return {
            "regular_price": str(record.lst_price),
        }

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        return {"sku": record.default_code or None}

    @changed_by("is_published")
    @mapping
    def status(self, record):
        return {
            "status": "publish" if record.active and record.is_published else "private"
        }

    @mapping
    def stock(self, record):
        if record.type in ("consu", "service"):
            stock = {
                "manage_stock": False,
            }
        else:
            stock = {
                "manage_stock": True,
                # WooCommerce don't accept fractional quantities
                "stock_quantity": int(record.qty_available),
                "stock_status": "instock" if record.qty_available > 0 else "outofstock",
            }
        return stock

    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.template")
        values = binder.get_external_dict_ids(record.product_tmpl_id)
        return {"parent_id": values["id"]}

    @mapping
    def image(self, record):
        # WooCommerce only allows one image per variant product
        if record.product_attachment_ids and self.collection.wordpress_backend_id:
            with self.collection.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                exporter = work.component(self._usage)
                binder = exporter.binder_for("wordpress.ir.attachment")
                if record.product_attachment_ids:
                    image = record.product_attachment_ids[0].attachment_id
                    values = binder.get_external_dict_ids(
                        image, check_external_id=False
                    )
                    if (
                        not values
                        and self.backend_record.wordpress_backend_id.test_database
                    ):
                        return
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
