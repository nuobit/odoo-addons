# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.template.export.mapper"

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
            # TODO: REVIEW: can we send two values as a list?
            for obb in other_binding_backend:
                translation_of = obb.woocommerce_idproduct
            return {"translation_of": translation_of}

    def _get_product_description(self, record):
        # We don't need check backend_record lang
        # because record already has lang on context
        return record.public_description

    def _get_product_variant_description(self, record):
        # We don't need check backend_record lang
        # because record already has lang on context
        return record.product_variant_id.variant_public_description

    def _get_value_ids(self, attribute_line):
        # TODO: It's in the correct lang?
        return attribute_line.value_ids.mapped("name")
