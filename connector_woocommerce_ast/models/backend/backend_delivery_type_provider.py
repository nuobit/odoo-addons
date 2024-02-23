# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class WooCommerceBackendDeliveryTypeProvider(models.Model):
    _name = "woocommerce.backend.delivery.type.provider"
    _description = "WooCommerce Backend Delivery Type Provider"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="woocommerce.backend",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def _get_selection_fields(self):
        return self.env["delivery.carrier"].fields_get(["delivery_type"])[
            "delivery_type"
        ]["selection"]

    delivery_type = fields.Selection(
        selection="_get_selection_fields",
    )
    woocommerce_provider = fields.Char(
        string="WooCommerce provider name",
        required=True,
    )

    _sql_constraints = [
        (
            "tax_map_uniq",
            "unique(backend_id, delivery_type)",
            "A binding already exists with the same (backend, carrier_id) ID.",
        ),
    ]
