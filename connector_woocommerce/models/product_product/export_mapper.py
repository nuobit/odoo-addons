# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WooCommerceProductProductExportMapper(Component):
    _name = "woocommerce.product.product.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.product"

    # @mapping
    # def name(self, record):
    #     if not len(record.product_tmpl_id.product_variant_ids) > 1:
    #         return {"name": record.name}

    @mapping
    def price(self, record):
        return {"price": record.lst_price}

    @mapping
    def sku(self, record):
        return {"sku": record.default_code or ''}

    @mapping
    def parent_id(self, record):
        # TODO: descomentar
        parent = record.product_tmpl_id
        external_id = self.binder_for("woocommerce.product.template").to_external(
            parent, wrap=False
        )
        self.check_external_id(external_id, parent)
        return {"parent_id": external_id}

    @mapping
    def images(self, record):
        im1 = self.env['ir.attachment'].search(
            [
                "&", "&",
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('res_field', '=', 'image_variant_1920'),
            ]
        )
        im2 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', record.product_variant_image_ids._name),
                ('res_id', 'in', record.product_variant_image_ids.ids),
                ('res_field', '=', 'image_1920'),

            ]
        )
        img_list = []
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

        # TODO: descomentar
    # @mapping
    # def attributes(self, record):
        # attr_list = []
        # for x in record.product_template_attribute_value_ids:
        #     attribute = self.binder_for("woocommerce.product.attribute").to_external(
        #         x.attribute_id, wrap=False
        #     )
        #     self.check_external_id(attribute, x.attribute_id)
        #     attr_list.append(
        #         {
        #             "id": attribute,
        #             "option": x.name,
        #         }
        #     )
        # return {"attributes": attr_list}
