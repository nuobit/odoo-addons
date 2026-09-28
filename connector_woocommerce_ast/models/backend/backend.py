# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
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

    def _get_export_eta(self, record):
        self.ensure_one()
        picking = record._get_woocommerce_tracking_picking()
        if picking:
            carrier = self.carrier_provider_ids.filtered(
                lambda x: x.delivery_type == picking.carrier_id.delivery_type
            )[:1]
            if carrier.tracking_export_delay > 0:
                return carrier.tracking_export_delay
        return super()._get_export_eta(record)
