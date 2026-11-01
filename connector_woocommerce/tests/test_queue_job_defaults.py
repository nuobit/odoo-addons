# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from .common import WooCommerceCase


class TestQueueJobDefaults(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.binding_model = cls.env["woocommerce.product.template"]

    def test_with_delay_uses_connector_default(self):
        job = self._new_job(
            "woocommerce.product.template",
            "export_batch",
            lambda: self.binding_model.with_delay().export_batch(self.backend),
        )
        self.assertEqual(job.max_retries, 20)

    def test_delayable_uses_connector_default(self):
        job = self._new_job(
            "woocommerce.product.template",
            "export_batch",
            lambda: self.binding_model.delayable().export_batch(self.backend).delay(),
        )
        self.assertEqual(job.max_retries, 20)

    def test_explicit_max_retries_wins(self):
        job = self._new_job(
            "woocommerce.product.template",
            "export_batch",
            lambda: self.binding_model.with_delay(max_retries=7).export_batch(
                self.backend
            ),
        )
        self.assertEqual(job.max_retries, 7)

    def test_explicit_zero_max_retries_wins(self):
        job = self._new_job(
            "woocommerce.product.template",
            "export_batch",
            lambda: self.binding_model.with_delay(max_retries=0).export_batch(
                self.backend
            ),
        )
        self.assertEqual(job.max_retries, 0)

    def test_other_job_options_are_forwarded(self):
        eta = datetime(2030, 1, 1, 12, 0, 0)
        job = self._new_job(
            "woocommerce.product.template",
            "export_batch",
            lambda: self.binding_model.with_delay(
                priority=5,
                eta=eta,
                description="Export the bound templates",
                channel="root",
                identity_key="export-bound-templates",
            ).export_batch(self.backend),
        )
        self.assertEqual(job.max_retries, 20)
        self.assertEqual(job.priority, 5)
        self.assertEqual(job.eta, eta)
        self.assertEqual(job.name, "Export the bound templates")
        self.assertEqual(job.channel, "root")
        self.assertEqual(job.identity_key, "export-bound-templates")

    def test_model_outside_connector_keeps_queue_default(self):
        job = self._new_job(
            "product.template",
            "write",
            lambda: self.template.with_delay().write({"name": "Renamed by a job"}),
        )
        self.assertEqual(job.max_retries, 5)
