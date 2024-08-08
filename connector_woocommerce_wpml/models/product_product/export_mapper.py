# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


class WooCommerceProductProductExportMapper(Component):
    _inherit = "woocommerce.product.product.export.mapper"

    # TODO: REMOVE THIS COMMENT: we need lang on write because woocommerce
    #  can't be write name with id as a external_id, we need name+lang.
    # TODO: REMOVE THIS LANG FROM MAPPER!!
    # @only_create
    @changed_by("lang")
    @mapping
    def lang(self, record):
        # TODO: unify this code. Probably do a function in res lang
        lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        return {"lang": lang}

    @only_create
    @mapping
    def translation_of(self, record):
        lang_code = record._context.get("lang")
        if lang_code:
            other_binding_backend = record.woocommerce_bind_ids.filtered(
                lambda x: x.backend_id == self.backend_record
                and x.woocommerce_lang
                != self.env["res.lang"]._get_wpml_code_from_iso_code(
                    record._context.get("lang")
                )
            )
            translation_of = None
            for obb in other_binding_backend:
                translation_of = obb.woocommerce_idproduct
            return {"translation_of": translation_of}

    def _get_product_description(self, record):
        # We don't need check backend_record lang
        # because record already has lang on context
        return record.variant_public_description

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
