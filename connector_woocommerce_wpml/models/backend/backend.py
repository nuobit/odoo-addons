# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WooCommerceBackend(models.Model):
    _inherit = "woocommerce.backend"

    language_ids = fields.Many2many(
        string="Languages for WPML",
        comodel_name="res.lang",
    )

    @api.constrains("language_ids")
    def check_language_ids(self):
        for rec in self:
            for lang in rec.language_ids:
                if not lang.wordpress_wpml_lang_code:
                    raise ValidationError(
                        _(
                            "The language %s has no WPML code, please define "
                            "this code in language before using it." % lang.name
                        )
                    )
