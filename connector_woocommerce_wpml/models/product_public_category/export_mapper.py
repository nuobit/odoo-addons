# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


class WooCommerceWPMLProductPublicCategoryExportMapper(Component):
    _name = "woocommerce.wpml.product.public.category.export.mapper"
    _inherit = "woocommerce.wpml.export.mapper"

    _apply_on = "woocommerce.wpml.product.public.category"
    # _inherit = "woocommerce.product.public.category.export.mapper"

    @changed_by("name")
    @mapping
    def name(self, record):
        if "  " in record.name:
            raise ValidationError(
                _(
                    "The category '%s' has a double space in the name. "
                    "WooCommerce only allow one space. Please, remove it before export."
                )
                % record.name
            )
        return {"name": record.name}

    @mapping
    def description(self, record):
        return {"description": record.description or None}

    # TODO: REMOVE THIS LANG FROM MAPPER!!
    @changed_by("lang")
    @mapping
    def lang(self, record):
        lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        return {"lang": lang}

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
                translation_of = obb.woocommerce_wpml_idpubliccategory
            return {"translation_of": translation_of}

    def _get_slug_name(self, record):
        return record.slug_name
