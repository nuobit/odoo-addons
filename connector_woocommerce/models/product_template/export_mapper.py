# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductTemplateExportMapper(Component):
    _name = "woocommerce.product.template.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.template"

    @mapping
    def name(self, record):
        return {"name": record.name}

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        default_codes = record.product_variant_ids.filtered("default_code").mapped(
            "default_code"
        )
        return {"sku": default_codes or None}

    @mapping
    def status(self, record):
        return {
            "status": "publish" if record.active and record.is_published else "private"
        }

    @mapping
    def stock(self, record):
        if record.type in ("consu", "service"):
            manage_stock = False
        else:
            manage_stock = True
        if len(record.product_variant_ids) <= 1:
            return {
                "manage_stock": manage_stock,
                # TODO: modificar la quantity per agafar les dels magatzems definits al backend
                "stock_quantity": int(record.product_variant_id.qty_available),
                "stock_status": "instock"
                if record.product_variant_id.qty_available > 0
                or record.type in ("consu", "service")
                else "outofstock",
            }
        else:
            return {
                "manage_stock": False,
            }

    @mapping
    def price(self, record):
        if len(record.product_variant_ids) <= 1:
            # On WooCommerce regular price is the usually price.
            # sales price is the price with discount.
            # On odoo we don't have this functionality per product
            return {
                "regular_price": str(record.list_price),
            }

    @mapping
    def description(self, record):
        description = False
        if record.public_description:
            description = record.with_context(
                lang=self.backend_record.backend_lang
            ).public_description
        elif (
            record.product_variant_ids == 1
            and record.product_variant_id.variant_public_description
        ):
            description = record.product_variant_id.with_context(
                lang=self.backend_record.backend_lang
            ).variant_public_description
        if description:
            return {"description": description}

    @mapping
    def product_type(self, record):
        product_type = "simple"
        if len(record.product_variant_ids) > 1:
            product_type = "variable"
        return {"type": product_type}

    @mapping
    def categories(self, record):
        categories = []
        binder = self.binder_for("woocommerce.product.public.category")
        for category in record.public_categ_ids:
            values = binder.get_external_dict_ids(category)
            categories.append({"id": values["id"]})
        if categories:
            return {"categories": categories}

    @mapping
    def attributes(self, record):
        binder = self.binder_for("woocommerce.product.attribute")
        attr_list = []
        for line in record.attribute_line_ids:
            values = binder.get_external_dict_ids(line.attribute_id)
            attr_list.append(
                {
                    "id": values["id"],
                    "options": line.value_ids.with_context(
                        lang=self.backend_record.backend_lang
                    ).mapped("name"),
                    "visible": "true",
                    "variation": "true",
                }
            )
        if attr_list:
            return {"attributes": attr_list}

    @mapping
    def images(self, record):
        if self.collection.wordpress_backend_id:
            with self.collection.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                exporter = work.component(self._usage)
                binder = exporter.binder_for("wordpress.ir.attachment")
                img_list = []
                if record.product_attachment_ids:
                    for image in record.product_attachment_ids.mapped("attachment_id"):
                        external_id = binder.get_external_dict_ids(
                            image, check_external_id=False
                        )
                        if external_id:
                            img_list.append(
                                {
                                    "id": external_id["id"],
                                }
                            )
                        else:
                            if (
                                self.backend_record.wordpress_backend_id
                                and not self.backend_record.wordpress_backend_id.test_database
                            ):
                                assert external_id, (
                                    "Unexpected error on %s:"
                                    "The backend id cannot be obtained."
                                    "At this stage, the backend record should "
                                    "have been already linked via "
                                    "._export_dependencies. " % record._name
                                )
                    if img_list:
                        return {"images": img_list}
