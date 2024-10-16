# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceProductTemplateExportMapper(Component):
    _name = "woocommerce.product.template.export.mapper"
    _inherit = "woocommerce.product.export.mapper"

    _apply_on = "woocommerce.product.template"

    @mapping
    def name(self, record):
        return {"name": record.website_name if record.website_name else record.name}

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        default_codes = (
            record.with_context(active_test=False)
            .product_variant_ids.filtered("default_code")
            .mapped("default_code")
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
        if any(
            [
                record.inventory_availability == "never",
                record.type in ("consu", "service"),
                record.has_attributes,
            ]
        ):
            stock = {
                "manage_stock": False,
                "stock_status": "instock",
            }
        else:
            if record.inventory_availability == "always":
                manage_stock = True
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
                stock = {
                    "manage_stock": manage_stock,
                    "stock_quantity": int(qty),
                    "stock_status": "instock"
                    if record.product_variant_id.qty_available > 0
                    or record.type in ("consu", "service")
                    else "outofstock",
                }
            else:
                raise ValidationError(
                    _(
                        "The inventory availability '%s' is not supported by WooCommerce. "
                        "Review product template {%s}%s."
                    )
                    % (record.inventory_availability, record.id, record.display_name)
                )
        return stock

    @mapping
    def price(self, record):
        if not record.has_attributes:
            # On WooCommerce regular price is the usually price.
            # sales price is the price with discount.
            # On odoo we don't have this functionality per product
            return {
                "regular_price": record.list_price,
            }
        return {"regular_price": None}

    @mapping
    def sale_price(self, record):
        if not record.has_attributes:
            pricelist = self.backend_record.discount_pricelist_id
            if pricelist:
                return {
                    "sale_price": pricelist.price_get(record.product_variant_id.id, 1)[
                        pricelist.id
                    ],
                }
        return {"sale_price": None}

    def _get_product_description(self, record):
        description = record.with_context(
            lang=self.backend_record.language_id.code
        ).public_description
        if not description:
            return False
        return tools.color_rgb2hex(description)

    def _get_product_variant_description(self, record):
        description = record.product_variant_id.with_context(
            lang=self.backend_record.language_id.code
        ).variant_public_description
        if not description:
            return False
        return tools.color_rgb2hex(description)

    @mapping
    def description(self, record):
        description = False
        if record.public_description:
            description = self._get_product_description(record)
        elif (
            len(record.product_variant_ids) == 1
            and record.product_variant_id.variant_public_description
        ):
            description = self._get_product_variant_description(record)
        return {"description": description if description else ""}

    def _get_short_description(self, record):
        return record.with_context(
            lang=self.backend_record.language_id.code
        ).public_short_description

    @mapping
    def short_description(self, record):
        short_description = []
        public_short_description = self._get_short_description(record)
        if public_short_description:
            short_description.append(public_short_description)
        document_description = self._prepare_document_description(record.document_ids)
        if document_description:
            short_description.append(document_description)
        return {"short_description": "\n".join(short_description) or None}

    @mapping
    def product_type(self, record):
        return {"type": "variable" if record.has_attributes else "simple"}

    @mapping
    def categories(self, record):
        categories = []
        binder = self.binder_for("woocommerce.product.public.category")
        for category in record.public_categ_ids:
            values = binder.get_external_dict_ids(category)
            categories.append({"id": values["id"]})
        if categories:
            return {"categories": categories}

    def _get_value_ids(self, attribute_line):
        return attribute_line.value_ids.with_context(
            lang=self.backend_record.language_id.code
        ).mapped("name")

    @mapping
    def attributes(self, record):
        binder = self.binder_for("woocommerce.product.attribute")
        attr_list = []
        for line in record.attribute_line_ids:
            values = binder.get_external_dict_ids(line.attribute_id)
            attr_list.append(
                {
                    "id": values["id"],
                    "options": self._get_value_ids(line),
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
                raise ValidationError(
                    _(
                        "Only one tax is allowed per product. "
                        "Please review taxes in product {%s} %s"
                    )
                    % (record.id, record.display_name)
                )
            tax_class = self.backend_record.tax_class_ids.filtered(
                lambda x: record["taxes_id"] == x.account_tax
            )
            if not tax_class:
                raise ValidationError(
                    _("Tax class is not defined on backend for tax %s")
                    % record.mapped("taxes_id").name
                )
            return {"tax_class": tax_class.woocommerce_tax_class}

    @mapping
    def upsell_ids(self, record):
        binder = self.binder_for("woocommerce.product.template")
        alternate_list = []
        if record.alternative_product_ids and not record.env.context.get(
            "export_wo_alt_p"
        ):
            for product in record.alternative_product_ids:
                values = binder.get_external_dict_ids(product)
                alternate_list.append(values["id"])
        return {"upsell_ids": alternate_list}

    @mapping
    def cross_sell_ids(self, record):
        product_binder = self.binder_for("woocommerce.product.product")
        template_binder = self.binder_for("woocommerce.product.template")
        accessory_list = []
        if record.accessory_product_ids and not record.env.context.get(
            "export_wo_acc_p"
        ):
            for product in record.accessory_product_ids:
                if product.product_tmpl_id.has_attributes:
                    values = product_binder.get_external_dict_ids(product)
                else:
                    values = template_binder.get_external_dict_ids(
                        product.product_tmpl_id
                    )
                accessory_list.append(values["id"])
        return {"cross_sell_ids": accessory_list}

    @mapping
    def images(self, record):
        if self.backend_record.wordpress_backend_id:
            with self.backend_record.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                binder = work.component(usage="binder")
                img_list = []
                product_image_attachments = record.with_context(
                    include_main_product_image=self.backend_record.use_main_product_image
                ).product_image_attachment_ids
                for image in product_image_attachments.mapped("attachment_id"):
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
                        if not self.backend_record.wordpress_backend_id.test_database:
                            assert external_id, (
                                "Unexpected error on %s:"
                                "The backend id cannot be obtained."
                                "At this stage, the backend record should "
                                "have been already linked via "
                                "._export_dependencies. " % record._name
                            )
                if img_list:
                    return {"images": img_list}
                else:
                    return {"images": []}

    def _get_slug_name(self, record):
        return record.with_context(lang=self.backend_record.language_id.code).slug_name

    @mapping
    def slug(self, record):
        slug = self._get_slug_name(record)
        if slug:
            return {"slug": slug}
