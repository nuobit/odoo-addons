# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WooCommerceProductTemplateExportMapper(Component):
    _name = "woocommerce.product.template.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.template"

    @mapping
    def name(self, record):
        return {"name": record.name}

    @mapping
    def price(self, record):
        return {"price": record.list_price}

    @mapping
    def description(self, record):
        if record.description:
            return {"description": record.description}

    @mapping
    def sku(self, record):
        if record.default_code:
            return {"sku": record.default_code}

    @mapping
    def product_type(self, record):
        product_type = "simple"
        if len(record.product_variant_ids) > 1:
            product_type = "variable"
        return {"type": product_type}

    # TODO:DESCOMENTAR
    # @mapping
    # def categories(self, record):
    #     categories = []
    #     for category in record.public_categ_ids:
    #         external_id = self.binder_for("woocommerce.product.category").to_external(
    #             category, wrap=False
    #         )
    #         self.check_external_id(external_id, category)
    #         categories.append({"id": external_id})
    #     if categories:
    #         return {"categories": categories}

    # TODO:DESCOMENTAR
    # TODO: REVIEW IF WE NEED IMPLEMENT A CHILD TO DO THIS
    # @mapping
    # def attributes(self, record):
    #     attr_list = []
    #     for line in record.attribute_line_ids:
    #         attribute_external_id = self.binder_for(
    #             "woocommerce.product.attribute"
    #         ).to_external(line.attribute_id, wrap=False)
    #         self.check_external_id(attribute_external_id, line)
    #         attr_list.append(
    #             {
    #                 "id": attribute_external_id,
    #                 "options": line.value_ids.mapped("name"),
    #                 "visible": "true",
    #                 "variation": "true",
    #             }
    #         )
    #     return {"attributes": attr_list}

    @mapping
    def images(self, record):
        img_list = []
        im1 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('res_field', '=', 'image_1920'),
            ]
        )
        im2 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', record.product_template_image_ids._name),
                ('res_id', 'in', record.product_template_image_ids.ids),
                ('res_field', '=', 'image_1920'),

            ]
        )
        for image in im1 + im2:
            external_id = self.binder_for("wordpress.ir.attachment").to_external(
                image, wrap=False
            )
            self.check_external_id(external_id, image)
            img_list.append(
                {
                    "id": external_id,
                }
            )
        return {"images": img_list}
