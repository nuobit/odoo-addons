# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import requests

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import RetryableJobError


class WooCommerceSaleOrderExportMapper(Component):
    _inherit = "woocommerce.sale.order.export.mapper"

    @mapping
    def status(self, record):
        result = super().status(record)
        if record.woocommerce_order_state == "partial_shipped":
            result["status"] = "partial-shipped"
        elif record.woocommerce_order_state == "delivered":
            result["status"] = "delivered"

        picking = record.picking_ids.filtered(
            lambda p: p.state == "done" and p.carrier_id
        ).sorted(key=lambda p: p.id)[-1:]
        if picking:
            backend_carrier = self.backend_record.carrier_provider_ids.filtered(
                lambda x: picking.carrier_id.delivery_type == x.delivery_type
            )
            if backend_carrier:
                if len(backend_carrier) > 1:
                    raise ValidationError(_("Carrier is duplicated"))
                if backend_carrier.use_tracking_number:
                    if picking.carrier_tracking_ref:
                        result["_wc_shipment_tracking_items"] = [
                            {
                                "tracking_provider": backend_carrier.woocommerce_provider,
                                "tracking_number": picking.carrier_tracking_ref,
                            }
                        ]
                        if backend_carrier.url:
                            check_url = backend_carrier.url.format(
                                tracking_ref=picking.carrier_tracking_ref
                            )
                            try:
                                response = requests.get(check_url, timeout=10)
                                response.raise_for_status()
                            except requests.RequestException as e:
                                raise RetryableJobError(
                                    _(
                                        "Tracking %s is not yet publicly "
                                        "available at %s: %s. Retrying."
                                    )
                                    % (
                                        picking.carrier_tracking_ref,
                                        check_url,
                                        e,
                                    ),
                                ) from e
                    else:
                        raise RetryableJobError(
                            _(
                                "Carrier %s requires a tracking number but "
                                "picking %s has none yet. Retrying."
                            )
                            % (picking.carrier_id.name, picking.name),
                        )

        return result
