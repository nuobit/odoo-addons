# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceProductProductExportMapper(Component):
    _name = "woocommerce.product.product.export.mapper"
    _inherit = "woocommerce.product.export.mapper"

    _apply_on = "woocommerce.product.product"

    @mapping
    def price(self, record):
        # On WooCommerce regular price is the usually price.
        # sales price is the price with discount.
        # On odoo we don't have this functionality per product
        return {
            "regular_price": record.lst_price,
        }

    @mapping
    def sale_price(self, record):
        pricelist = self.backend_record.discount_pricelist_id
        if pricelist:
            return {
                "sale_price": pricelist.price_get(record.id, 1)[pricelist.id],
            }
        return {"sale_price": None}

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        # This requirement is not needed on WooCommerce
        # but it's necessary in e-commerce
        if not record.default_code:
            raise ValidationError(
                _("You must define an internal reference for the product {%s}'%s'")
                % (record.id, record.display_name)
            )
        return {"sku": record.default_code}

    @changed_by("is_published")
    @mapping
    def status(self, record):
        return {
            "status": "publish"
            if record.active and record.variant_is_published
            else "private"
        }

    @mapping
    def stock(self, record):
        if (
            record.type in ("consu", "service")
            or record.variant_inventory_availability == "never"
        ):
            stock = {"manage_stock": False, "stock_status": "instock"}
        # modificar el type
        elif record.variant_inventory_availability == "always":
            qty = sum(
                self.env["stock.quant"]
                .search(
                    [
                        ("product_id", "=", record.id),
                        (
                            "location_id",
                            "child_of",
                            self.backend_record.stock_location_ids.ids,
                        ),
                    ]
                )
                .mapped("available_quantity")
            )
            stock = {
                "manage_stock": True,
                # WooCommerce don't accept fractional quantities
                "stock_quantity": int(qty),
                "stock_status": "instock" if record.qty_available > 0 else "outofstock",
            }
        else:
            raise ValidationError(
                _(
                    "The inventory availability '%s' is not supported by WooCommerce. "
                    "Review product variant {%s}%s."
                )
                % (
                    record.variant_inventory_availability,
                    record.id,
                    record.display_name,
                )
            )
        return stock

    def _get_product_description(self, record):
        description = record.with_context(
            lang=self.backend_record.language_id.code
        ).variant_public_description
        if not description:
            return False
        return tools.color_rgb2hex(description)

    @mapping
    def description(self, record):
        description = []
        product_description = self._get_product_description(record)
        if product_description:
            description.append(product_description)
        if record.document_ids:
            document_description = self._prepare_document_description(
                record.document_ids
            )
            if document_description:
                description.append(document_description)
        return {"description": "\n".join(description) or None}

    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.template")
        values = binder.get_external_dict_ids(record.product_tmpl_id)
        return {"parent_id": values["id"]}

    @mapping
    def image(self, record):
        # WooCommerce only allows one image per variant product
        product_image_attachments = record.with_context(
            include_main_product_image=self.backend_record.use_main_product_image
        ).product_variant_image_attachment_ids
        if product_image_attachments and self.backend_record.wordpress_backend_id:
            with self.backend_record.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                binder = work.component(usage="binder")
                image = product_image_attachments[0].attachment_id
                values = binder.get_external_dict_ids(image, check_external_id=False)
                if (
                    self.backend_record.wordpress_backend_id.test_database
                    and not values
                ):
                    return None
                return {
                    "image": {
                        "id": values["id"],
                    }
                }
        else:
            return {"image": {}}

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
