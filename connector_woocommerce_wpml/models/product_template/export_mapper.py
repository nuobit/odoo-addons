# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.template.export.mapper"

    @changed_by("lang")
    @mapping
    def lang(self, record):
        # TODO: unify this code. Probably do a function in res lang
        lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        return {"lang": lang}

    @mapping
    def translation_of(self, record):
        lang_code = record._context.get("lang")
        if lang_code:
            source_lang_code = self.backend_record.language_ids[0].code
            if lang_code == source_lang_code:
                # We don't need to set translation_of for the default lang
                return {}
            else:
                wpml_code = self.env["res.lang"]._get_wpml_code_from_iso_code(
                    source_lang_code
                )
                master_binding_backend = record.woocommerce_bind_ids.filtered(
                    lambda x: x.backend_id == self.backend_record
                    and x.woocommerce_lang == wpml_code
                )
                translation_of = None
                if master_binding_backend:
                    translation_of = master_binding_backend.woocommerce_idproduct
                return {"translation_of": translation_of}

    def _get_product_description(self, record):
        # We don't need check backend_record lang
        # because record already has lang on context
        return tools.color_rgb2hex(record.public_description)

    def _get_short_description(self, record):
        return record.public_short_description

    def _get_product_variant_description(self, record):
        # We don't need check backend_record lang
        # because record already has lang on context
        return tools.color_rgb2hex(record.product_variant_id.variant_public_description)

    def _get_value_ids(self, attribute_line):
        return attribute_line.product_template_value_ids.mapped("name")

    def _get_slug_name(self, record):
        return record.slug_name
