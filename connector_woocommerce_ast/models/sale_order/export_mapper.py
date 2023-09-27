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
        if record.woocommerce_order_state == "partial-shipped":
            return {"status": "partial-shipped"}
        elif record.woocommerce_order_state == "delivered":
            return {"status": "delivered"}
        else:
            return super().status(record)

    def get_shippment(self, record):
        tracking = {}
        for picking in record.picking_ids:
            if picking.carrier_id:
                carrier = self.backend_record.carrier_provider_ids.filtered(
                    lambda x: picking.carrier_id.delivery_type == x.delivery_type
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
                return {"key": "_wc_shipment_tracking_items", "value": [tracking]}

    def _get_meta_data_values(self, record):
        values = super()._get_meta_data_values(record)
        shipment_values = self.get_shippment(record)
        if shipment_values:
            values.append(shipment_values)
        return values
