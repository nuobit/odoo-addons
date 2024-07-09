# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WooCommerceBackend(models.Model):
    _inherit = "woocommerce.backend"

    wpml_lang_map_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.mapping",
        inverse_name="backend_id",
        string="WPML Lang Mapping",
        required=True,
    )

    def _get_woocommerce_lang(self, lang_code):
        lang = self.wpml_lang_map_ids.filtered(lambda x: x.lang_id.code == lang_code)
        if lang:
            return lang.woocommerce_wpml_lang
        else:
            raise ValidationError(
                _("The language %s is not mapped to any WooCommerce language")
                % lang_code
            )

    def _get_odoo_iso_code(self, wpml_code):
        lang = self.wpml_lang_map_ids.filtered(
            lambda x: x.woocommerce_wpml_lang == wpml_code
        )
        if lang:
            return lang.lang_id.code
        else:
            raise ValidationError(
                _(
                    "The WooCommerce WPML language code %s is not mapped to any Odoo language"
                )
                % wpml_code
            )
