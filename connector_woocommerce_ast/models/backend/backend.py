# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceBackend(models.Model):
    _inherit = "woocommerce.backend"
    _description = "WooCommerce Backend"

    carrier_provider_ids = fields.One2many(
        comodel_name="woocommerce.backend.delivery.type.provider",
        inverse_name="backend_id",
        string="Carrier Provider",
    )
