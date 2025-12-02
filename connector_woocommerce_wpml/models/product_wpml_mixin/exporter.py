# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductWPMLMixinExporter(AbstractComponent):
    _name = "woocommerce.product.wpml.mixin.record.direct.exporter"
    _inherit = "connector.extension.generic.record.direct.exporter"

    def wpml_run(self, relation, always=True, internal_fields=None):
        res = []
        langs_to_export = self.backend_record.lang_ids.mapped("code")
        if not langs_to_export:
            raise ValidationError(
                _(
                    "You need to define at least one language to export "
                    "in the WooCommerce WPML Backend (%s)."
                )
                % self.backend_record.name
            )
        langs_first_default = sorted(
            langs_to_export,
            key=lambda lang: (lang != self.backend_record.language_id.code, lang),
        )
        first_lang = True
        for lang in langs_first_default:
            result = super().run(
                relation.with_context(lang=lang, first_lang=first_lang),
                always=always,
                internal_fields=internal_fields,
            )
            res.append(result)
            if first_lang:
                first_lang = False
        return res
