# Copyright 2026 NuoBiT Solutions, S.L. - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def mrw_tracking_state_update(self, picking):
        result = super().mrw_tracking_state_update(picking)
        if picking.date_delivered and picking.tracking_state:
            picking.delivery_state = "customer_delivered"
        return result
