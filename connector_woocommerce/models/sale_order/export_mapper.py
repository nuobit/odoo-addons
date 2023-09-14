# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceSaleOrderExportMapper(Component):
    _name = "woocommerce.sale.order.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.sale.order"

    @mapping
    def status(self, record):
        if record.woocommerce_order_state == "processing":
            status = "on-hold" if record.state == "draft" else "processing"
        elif record.woocommerce_order_state == "done":
            status = "completed"
        else:
            status = "cancelled"
        return {"status": status}

    @mapping
    def picking(self, record):
        shipment = []
        tracking = {}
        for picking in record.picking_ids:
            if picking.carrier_id:
                carrier = self.backend_record.carrier_provider_ids.filtered(
                    lambda x: record["carrier_id"] == x.carrier_id
                )
                if not carrier:
                    raise ValidationError(
                        _("carrier is not defined on backend for tax %s")
                        % record.get("carrier_id")
                    )
                tracking["tracking_provider"] = carrier.woocommerce_provider
            if picking.carrier_tracking_ref:
                tracking["tracking_number"] = picking.carrier_tracking_ref
            if tracking:
                shipment.append(
                    {"key": "_wc_shipment_tracking_items", "value": [tracking]}
                )
        if shipment:
            return {"meta_data": shipment}
