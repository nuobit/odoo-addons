# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceBackendTaxClass(models.Model):
    _name = "woocommerce.wpml.backend.mapping"
    _description = "WooCommerce WPML Backend"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="woocommerce.backend",
        required=True,
        ondelete="cascade",
    )
    lang_id = fields.Many2one(
        comodel_name="res.lang",
        required=True,
    )
    woocommerce_wpml_lang = fields.Char(
        string="WooCommerce WPML Lang",
        required=True,
    )
    _sql_constraints = [
        (
            "tax_map_uniq",
            "unique(backend_id, woocommerce_wpml_lang)",
            "A binding already exists with the same (backend, woocommerce_wpml_lang) ID.",
        ),
        (
            "tax_map_uniq",
            "unique(backend_id, lang_id)",
            "A binding already exists with the same (backend, lang_id) ID.",
        ),
    ]
