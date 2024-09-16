# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceWPMLBackendAccountTax(models.Model):
    _name = "woocommerce.wpml.backend.account.tax"
    _inherit = "woocommerce.backend.account.tax"
    _description = "WooCommerce WPML Backend Account Tax"

    backend_id = fields.Many2one(
        comodel_name="woocommerce.wpml.backend",
    )
