# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.connector_woocommerce.tests.common import WooCommerceOrderCase


class WooCommerceAstCase(WooCommerceOrderCase):
    """Shop orders shipped by a carrier that the backend maps to a tracking
    provider."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "WooCommerce carrier",
                "delivery_type": "fixed",
                "product_id": cls.env["product.product"]
                .create({"name": "WooCommerce shipping", "type": "service"})
                .id,
            }
        )
        cls.provider = cls.env["woocommerce.backend.delivery.type.provider"].create(
            {
                "backend_id": cls.backend.id,
                "delivery_type": "fixed",
                "woocommerce_provider": "WooCommerce tracking provider",
                "use_tracking_number": True,
                "tracking_export_delay": 300,
            }
        )

    def setUp(self):
        super().setUp()
        # The carrier answers each shipment with a tracking number: its name.
        patcher = patch.object(
            type(self.env["delivery.carrier"]),
            "fixed_send_shipping",
            side_effect=lambda pickings: [
                {"exact_price": 0.0, "tracking_number": picking.name}
                for picking in pickings
            ],
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _create_order(self, quantities):
        """A shop order shipped by the carrier."""
        order = super()._create_order(quantities)
        order.carrier_id = self.carrier
        return order

    def _carrier_reports(self, pickings, delivery_state):
        """The carrier reports ``delivery_state`` for each of ``pickings`` when
        their tracking is updated. A fixed carrier has no tracking of its own,
        so the test gives it one."""
        with patch.object(
            type(self.env["delivery.carrier"]),
            "fixed_tracking_state_update",
            create=True,
            side_effect=lambda picking: picking.write(
                {"delivery_state": delivery_state}
            ),
        ):
            pickings.tracking_state_update()
