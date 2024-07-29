# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create
from odoo.addons.connector_extension.components.mapper import required


class WooCommerceProductAttributeValueExportMapper(Component):
    _inherit = "woocommerce.product.attribute.value.export.mapper"

    @required("name")
    @changed_by("name")
    @mapping
    def name(self, record):
        dict_name = super().name(record)
        if "name" in dict_name:
            if dict_name["name"] != record.name:
                dict_name["name"] = record.name
        return dict_name

    @required("parent_id")
    @changed_by("attribute_id")
    @mapping
    def parent_id(self, record):
        parent_dict = super().parent_id(record)
        if "parent_id" in parent_dict:
            parent_dict["parent_id"] = parent_dict["parent_id"]
        binder = self.binder_for("woocommerce.product.attribute")
        values = binder.get_external_dict_ids(record.attribute_id)
        return {"parent_id": values["id"] or None}

    @changed_by("attribute_id")
    @mapping
    def parent_name(self, record):
        dict_name = super().parent_name(record)
        if "parent_name" in dict_name:
            if dict_name["parent_name"] != record.attribute_id.name:
                dict_name["parent_name"] = record.attribute_id.name
        return dict_name

    @changed_by("lang")
    @mapping
    def lang(self, record):
        lang_code = record._context.get("lang")
        return {"lang": self.backend_record._get_woocommerce_lang(lang_code)}

    @only_create
    @mapping
    def translation_of(self, record):
        lang_code = record._context.get("lang")
        if lang_code:
            other_binding_backend = record.woocommerce_bind_ids.filtered(
                lambda x: x.backend_id == self.backend_record
                and x.woocommerce_lang
                != self.backend_record._get_woocommerce_lang(lang_code)
            )
            translation_of = None
            for obb in other_binding_backend:
                translation_of = obb.woocommerce_idattributevalue
            return {"translation_of": translation_of}
