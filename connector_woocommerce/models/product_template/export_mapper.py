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

    # TODO: mirar como trata odoo el tema de dos variantes archivadas
    #  y una sin archivar. trata a ese producto como variante?
    # TODO mirar de recuperar los productos archivados al hacer estas consultas
    @changed_by("default_code")
    @mapping
    def sku(self, record):
        return {
            "sku": record.product_variant_ids.filtered("default_code").mapped(
                "default_code"
            )
        }

    @mapping
    def status(self, record):
        if record.active:
            return {"status": "publish"}
        else:
            return {"status": "pending"}

    @mapping
    def stock(self, record):
        if len(record.product_variant_ids) == 1:
            return {
                "manage_stock": True,
                "stock_quantity": record.product_variant_id.qty_available,
                "stock_status": "instock"
                if record.product_variant_id.qty_available > 0
                else "outofstock",
            }
        else:
            return {
                "manage_stock": False,
            }

    @mapping
    def price(self, record):
        if len(record.product_variant_ids) == 1:
            # # TODO: Revisar esto, el sale price no se exporta si es igual
            #  que el regular. si el regular no esta informado, no se exporta.
            # El regular price deberia ser menor
            # que el regular, si no tampoco se exporta.
            return {
                "regular_price": str(record.list_price),
                "sale_price": str(record.list_price),
            }

    @mapping
    def description(self, record):
        if record.description:
            return {"description": record.description}

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
                im1 = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", record._name),
                        ("res_id", "=", record.id),
                        ("res_field", "=", "image_1920"),
                    ]
                )
                im2 = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", record.product_template_image_ids._name),
                        ("res_id", "in", record.product_template_image_ids.ids),
                        ("res_field", "=", "image_1920"),
                    ]
                )
                for image in im1 + im2:
                    external_id = binder.get_external_dict_ids(image)
                    img_list.append(
                        {
                            "id": external_id["id"],
                        }
                    )
                return {"images": img_list}


# TODO: asi funcionaria? nos ahorrariamos un search
# im1_domain = [
#     ("res_model", "=", record._name),
#     ("res_id", "=", record.id),
#     ("res_field", "=", "image_1920"),
# ]
#
# im2_domain = [
#     ("res_model", "=", record.product_template_image_ids._name),
#     ("res_id", "in", record.product_template_image_ids.ids),
#     ("res_field", "=", "image_1920"),
# ]
#
# all_images = self.env["ir.attachment"].search(im1_domain + im2_domain)
