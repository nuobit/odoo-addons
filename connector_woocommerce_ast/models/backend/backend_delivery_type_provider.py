# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
    use_tracking_number = fields.Boolean(
        string="Use tracking number",
        default=False,
        help="Export tracking information for this provider and delay the "
        "WooCommerce status export until the picking has a tracking number.",
    )
    tracking_export_delay = fields.Integer(
        string="Tracking export delay (seconds)",
        default=0,
        help="Per-carrier override of the backend tracking_export_delay. "
        "If set to a positive value, this delay is used for this carrier "
        "instead of the backend default.",
    )

    @api.constrains("tracking_export_delay")
    def _check_tracking_export_delay(self):
        for rec in self:
            if rec.tracking_export_delay < 0:
                raise ValidationError(_("Tracking export delay must be 0 or positive."))

    _sql_constraints = [
        (
            "tax_map_uniq",
            "unique(backend_id, delivery_type)",
            "A binding already exists with the same (backend, carrier_id) ID.",
        ),
    ]
