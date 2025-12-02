# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.connector_extension.common import tools


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
    #         source_lang_code = self.backend_record.lang_ids[0].code
    #         if lang_code == source_lang_code:
    #             # We don't need to set translation_of for the default lang
    #             return {}
    #         else:
    #             wpml_code = self.env["res.lang"]._get_wpml_code_from_iso_code(
    #                 source_lang_code
    #             )
    #             master_binding_backend = record.woocommerce_bind_ids.filtered(
    #                 lambda x: x.backend_id == self.backend_record
    #                 and x.woocommerce_lang == wpml_code
    #             )
    #             translation_of = None
    #             if master_binding_backend:
    #                 translation_of = master_binding_backend.woocommerce_idproduct
    #             return {"translation_of": translation_of}

    # TDOO: Make this only_create
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

                return {"translation_of": master_binding.woocommerce_idproduct}

    def _get_product_description(self, record):
        res = False
        odoo_lang = record._context.get("lang")
        if not odoo_lang:
            raise ValidationError(_("Language must be always set"))
        if odoo_lang == self.backend_record.language_id.code:
            res = super()._get_product_description(record)
        else:
            # We don't need check backend_record lang
            # because record already has lang on context
            description = record.variant_public_description
            if description:
                res = tools.color_rgb2hex(description)
        return res

    @changed_by("default_code")
    @mapping
    def sku(self, record):
        binding = self.options["binding"] if self.options else None
        if binding:
            if binding.woocommerce_master_lang:
                return super().sku(record)
        else:
            master_binding = record.woocommerce_bind_ids.filtered(
                lambda x: x.backend_id == self.backend_record
                and x.woocommerce_master_lang
            )
            if master_binding:
                if len(master_binding) > 1:
                    raise ValidationError(
                        _(
                            "It should always be one and exactly one binding "
                            "with master language emabled"
                        )
                    )
            else:
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
                                "Unexpected!! The first language on creation should "
                                "be always the same defined in the backend."
                            )
                        )
                    return super().sku(record)

    # @mapping
    # def attributes(self, record):
    #     binder = self.binder_for("woocommerce.product.attribute")
    #     attr_list = []
    #     for value in record.product_template_attribute_value_ids:
    #         values = binder.get_external_dict_ids(value.attribute_id)
    #         attr_list.append(
    #             {
    #                 "id": values["id"],
    #                 "option": value.name,
    #             }
    #         )
    #     return {"attributes": attr_list}
