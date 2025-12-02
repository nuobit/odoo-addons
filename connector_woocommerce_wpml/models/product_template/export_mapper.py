# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

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
        binding = self.options["binding"]
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
                            "Unexpected. No master language found! On creation of "
                            "additional languages it should "
                            "always already exists the master language should be "
                            "always the same defined in the backend."
                        )
                    )

                return {"translation_of": master_binding.woocommerce_idproduct}

    # TODO: this is exactly the same in product_product, unify,
    # via inheritance or mixim, whatever
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
