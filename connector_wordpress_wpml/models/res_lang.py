# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Lang(models.Model):
    _inherit = "res.lang"

    wordpress_wpml_lang_code = fields.Char()

    _sql_constraints = [
        (
            "wordpress_wpml_lang_code_uniq",
            "unique(wordpress_wpml_lang_code)",
            "The WPML lang code must be unique !",
        ),
    ]

    @api.model
    def _get_wpml_code_from_iso_code(self, code):
        lang = self.env["res.lang"].search([("iso_code", "=", code)])
        if not lang:
            raise ValidationError(_("Language not found with code %s") % code)
        if not lang.wordpress_wpml_lang_code:
            raise ValidationError(_("WPML code not found for lang: %s") % lang)
        return lang.wordpress_wpml_lang_code

    @api.model
    def _get_iso_code_from_wpml_code(self, wpml_code):
        lang = self.env["res.lang"].search(
            [("wordpress_wpml_lang_code", "=", wpml_code)]
        )
        if not lang:
            raise ValidationError(_("Language not found with wpml code %s") % wpml_code)
        return lang.iso_code
