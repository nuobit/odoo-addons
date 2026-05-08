# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceSaleOrderExportMapper(Component):
    _inherit = "woocommerce.sale.order.export.mapper"

    @mapping
    def status(self, record):
        if record.woocommerce_order_state == "partial_shipped":
            return {"status": "partial-shipped"}
        elif record.woocommerce_order_state == "delivered":
            return {"status": "delivered"}
        else:
            return super().status(record)

    @mapping
    def shipment_tracking(self, record):
        tracking = {}
        picking = record.picking_ids.filtered(
            lambda p: p.state == "done" and p.carrier_id
        ).sorted(key=lambda p: p.id,)[-1:]
        if picking:
            carrier = self.backend_record.carrier_provider_ids.filtered(
                lambda x: picking.carrier_id.delivery_type == x.delivery_type
            )
            if not carrier:
                raise ValidationError(
                    _("carrier is not defined on backend for carrier %s")
                    % picking.carrier_id.name
                )
            elif len(carrier) > 1:
                raise ValidationError(_("Carrier is duplicated"))
            if not (carrier.use_tracking_number and not picking.carrier_tracking_ref):
                tracking["tracking_provider"] = carrier.woocommerce_provider
                if picking.carrier_tracking_ref:
                    tracking["tracking_number"] = picking.carrier_tracking_ref
        if tracking:
            return {"_wc_shipment_tracking_items": [tracking]}
