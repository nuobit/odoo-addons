# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

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
        if not default_codes:
            raise ValidationError(
                _("You must define a default code for the product %s") % record.name
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
            qty = sum(
                self.env["stock.quant"]
                .search(
                    [
                        ("product_id", "=", record.product_variant_id.id),
                        (
                            "location_id",
                            "child_of",
                            self.backend_record.stock_location_ids.ids,
                        ),
                    ]
                )
                .mapped("available_quantity")
            )
            return {
                "manage_stock": manage_stock,
                # TODO: modificar la quantity per agafar les dels magatzems definits al backend
                "stock_quantity": int(qty),
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
                "regular_price": record.list_price,
            }

    @mapping
    def description(self, record):
        description = False
        if record.public_description:
            description = record.with_context(
                lang=self.backend_record.language_id.code
            ).public_description
        elif (
            len(record.product_variant_ids) == 1
            and record.product_variant_id.variant_public_description
        ):
            description = record.product_variant_id.with_context(
                lang=self.backend_record.language_id.code
            ).variant_public_description
        return {"description": description if description else ""}

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
                        lang=self.backend_record.language_id.code
                    ).mapped("name"),
                    "visible": "true",
                    "variation": "true",
                }
            )
        if attr_list:
            return {"attributes": attr_list}

    @mapping
    def tax_class(self, record):
        if record.taxes_id:
            if len(record.taxes_id) > 1:
                raise ValidationError(_("Only one tax is allowed per product"))
            tax_class = self.backend_record.tax_class_ids.filtered(
                lambda x: record["taxes_id"] == x.account_tax
            )
            if not tax_class:
                raise ValidationError(
                    _("Tax class is not defined on backend for tax %s")
                    % record.mapped("taxes_id").name
                )
            return {"tax_class": tax_class.woocommerce_tax_class}

    # @mapping
    # def upsell_ids(self, record):
    #     binder = self.binder_for("woocommerce.product.template")
    #     alternate_list = []
    #     if record.alternative_product_ids:
    #         for product in record.alternative_product_ids:
    #             values = binder.get_external_dict_ids(product)
    #             alternate_list.append(values["id"])
    #     if alternate_list:
    #         # return {"cross_sell_ids": alternate_list}
    #         return {"upsell_ids": alternate_list}
    #
    # @mapping
    # def cross_sell_ids(self, record):
    #     binder = self.binder_for("woocommerce.product.product")
    #     accessory_list = []
    #     if record.accessory_product_ids:
    #         for product in record.accessory_product_ids:
    #             values = binder.get_external_dict_ids(product)
    #             accessory_list.append(values["id"])
    #     if accessory_list:
    #         return {"cross_sell_ids": accessory_list}

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
