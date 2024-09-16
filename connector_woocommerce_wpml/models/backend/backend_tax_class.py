# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceWPMLBackendTaxClass(models.Model):
    _name = "woocommerce.wpml.backend.tax.class"
    _inherit = "woocommerce.backend.tax.class"
    _description = "WooCommerce Backend Tax Class"

    backend_id = fields.Many2one(
        comodel_name="woocommerce.wpml.backend",
    )
