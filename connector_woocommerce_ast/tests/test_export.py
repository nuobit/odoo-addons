# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from .common import WooCommerceAstCase


class TestExport(WooCommerceAstCase):
    def test_done_delivery_queues_the_export_after_the_carrier_delay(self):
        order = self._create_order({self.product_1: 1})
        self._bind_order(order, 3001)
        order.action_confirm()
        self.assertEqual(order.woocommerce_order_state, "processing")
        with freeze_time("2030-01-01 12:00:00"):
            job = self._new_job(
                "woocommerce.sale.order",
                "export_batch",
                lambda: self._validate(order.picking_ids),
            )
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(job.eta, datetime(2030, 1, 1, 12, 5, 0))

    def test_done_delivery_exports_its_tracking(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        self._validate(order.picking_ids)
        self.assertEqual(
            self._mapped_values("woocommerce.sale.order", order)[
                "_wc_shipment_tracking_items"
            ],
            [
                {
                    "tracking_provider": self.provider.woocommerce_provider,
                    "tracking_number": order.picking_ids.name,
                }
            ],
        )

    def test_return_updating_quantities_queues_no_export(self):
        order = self._create_order({self.product_1: 1})
        self._bind_order(order, 3001)
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        jobs = self._new_jobs(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._validate(return_picking),
        )
        self.assertFalse(jobs)

    def test_return_with_a_carrier_keeps_the_delivery_tracking(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        return_picking.carrier_id = self.carrier
        self._validate(return_picking)
        self.assertEqual(
            self._mapped_values("woocommerce.sale.order", order)[
                "_wc_shipment_tracking_items"
            ],
            [
                {
                    "tracking_provider": self.provider.woocommerce_provider,
                    "tracking_number": delivery.name,
                }
            ],
        )

    def test_return_with_another_carrier_keeps_the_delivery_delay(self):
        pickup_carrier = self.env["delivery.carrier"].create(
            {
                "name": "Pickup carrier",
                "delivery_type": "base_on_rule",
                "product_id": self.carrier.product_id.id,
            }
        )
        order = self._create_order({self.product_1: 1})
        self._bind_order(order, 3001)
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        return_picking.carrier_id = pickup_carrier
        self._validate(return_picking)
        with freeze_time("2030-01-01 12:00:00"):
            job = self._new_job(
                "woocommerce.sale.order",
                "export_batch",
                lambda: self._create_return(return_picking),
            )
        self.assertEqual(job.eta, datetime(2030, 1, 1, 12, 5, 0))
