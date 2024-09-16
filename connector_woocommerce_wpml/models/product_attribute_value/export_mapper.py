# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create
from odoo.addons.connector_extension.components.mapper import required


class WooCommerceWPMLProductAttributeValueExportMapper(Component):
    _name = "woocommerce.wpml.product.attribute.value.export.mapper"
    _inherit = "woocommerce.wpml.export.mapper"

    _apply_on = "woocommerce.wpml.product.attribute.value"
    # _inherit = "woocommerce.product.attribute.value.export.mapper"

    @required("name")
    @changed_by("name")
    @mapping
    def name(self, record):
        return {"name": record.name}

    @required("parent_id")
    @changed_by("attribute_id")
    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.wpml.product.attribute")
        values = binder.get_external_dict_ids(record.attribute_id)
        return {"parent_id": values["id"] or None}

    @changed_by("attribute_id")
    @mapping
    def parent_name(self, record):
        return {"parent_name": record.attribute_id.name}

    @changed_by("lang")
    @mapping
    def lang(self, record):
        return {
            "lang": self.env["res.lang"]._get_wpml_code_from_iso_code(
                record._context.get("lang")
            )
        }

    @only_create
    @mapping
    def translation_of(self, record):
        lang_code = record._context.get("lang")
        if lang_code:
            other_binding_backend = record.woocommerce_wpml_bind_ids.filtered(
                lambda x: x.backend_id == self.backend_record
                and x.woocommerce_lang
                != self.env["res.lang"]._get_wpml_code_from_iso_code(
                    record._context.get("lang")
                )
            )
            translation_of = None
            for obb in other_binding_backend:
                translation_of = obb.woocommerce_wpml_idattributevalue
            return {"translation_of": translation_of}
