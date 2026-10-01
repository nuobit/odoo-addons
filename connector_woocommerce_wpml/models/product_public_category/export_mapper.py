# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductPublicCategoryExportMapper(Component):
    _inherit = "woocommerce.product.public.category.export.mapper"

    # TODO: Make this only_create???
    @changed_by("lang")
    @mapping
    def lang(self, record):
        # TODO: unify this code. Probably do a function in res lang
        odoo_lang = record._context.get("lang")
        if not odoo_lang:
            raise ValidationError(_("Language must be always set"))
        wc_lang = self.env["res.lang"]._get_wpml_code_from_iso_code(odoo_lang)
        return {"lang": wc_lang}

    # @only_create
    # @mapping
    # def translation_of(self, record):
    #     lang_code = record._context.get("lang")
    #     if lang_code:
    #         other_binding_backend = record.woocommerce_bind_ids.filtered(
    #             lambda x: x.backend_id == self.backend_record
    #             and x.woocommerce_lang
    #             != self.env["res.lang"]._get_wpml_code_from_iso_code(
    #                 record._context.get("lang")
    #             )
    #         )
    #         translation_of = None
    #         for obb in other_binding_backend:
    #             translation_of = obb.woocommerce_idpubliccategory
    #         return {"translation_of": translation_of}

    # TODO: Make this only_create???
    @mapping
    def translation_of(self, record):
        binding = self.options["binding"] if self.options else None
        if not binding:
            if not record._context.get("lang"):
                raise ValidationError(_("Language must be always set"))
            if "first_lang" not in record._context:
                raise ValidationError(_("First lang must be always set on context"))
            if not isinstance(record._context["first_lang"], bool):
                raise ValidationError(_("First lang must be a boolean"))
            first_lang = record._context["first_lang"]
            if first_lang:
                odoo_lang = record._context["lang"]
                if odoo_lang != self.backend_record.language_id.code:
                    raise ValidationError(
                        _(
                            "Unexpected!! The first language on creation should be "
                            "always the same defined in the backend."
                        )
                    )
            else:
                other_bindings = record.woocommerce_bind_ids.filtered(
                    lambda x: x.backend_id == self.backend_record
                )
                if not other_bindings:
                    raise ValidationError(
                        _(
                            "Unexpected. No other bindings found when it should because"
                            " this is not the first language!!"
                        )
                    )
                master_binding = other_bindings.filtered(
                    lambda x: x.woocommerce_master_lang
                )
                if not master_binding:
                    raise ValidationError(
                        _(
                            "Unexpected. No Master language found! On creation "
                            "of additional languages it shoould "
                            "always already exists the master language should be "
                            "always the same defined in the backend."
                        )
                    )

                return {"translation_of": master_binding.woocommerce_idpubliccategory}

    # TODO: Try to don't repeat this code
    @changed_by("name")
    @mapping
    def name(self, record):
        dict_name = super().name(record)
        if "name" in dict_name:
            if dict_name["name"] != record.name:
                dict_name["name"] = record.name
        return dict_name

    @mapping
    def description(self, record):
        dict_description = super().description(record)
        if dict_description["description"] != record.description:
            dict_description["description"] = record.description or None
        return dict_description

    def _get_slug_name(self, record):
        return record.slug_name
