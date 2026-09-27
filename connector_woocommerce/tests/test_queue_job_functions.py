# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.queue_job.exception import FailedJobError, RetryableJobError
from odoo.addons.queue_job.job import Job

from .common import WooCommerceCase

RETRY_PATTERN = {1: (5, 15), 5: (20, 40), 10: (45, 75), 15: (240, 360)}

FUNCTIONS = [
    ("woocommerce.product.product", "export_batch", "root.woocommerce_export_batch"),
    ("woocommerce.product.product", "export_record", "root.woocommerce_export_record"),
    ("woocommerce.product.template", "export_batch", "root.woocommerce_export_batch"),
    ("woocommerce.product.template", "export_record", "root.woocommerce_export_record"),
    (
        "woocommerce.product.public.category",
        "export_batch",
        "root.woocommerce_export_batch",
    ),
    (
        "woocommerce.product.public.category",
        "export_record",
        "root.woocommerce_export_record",
    ),
    ("woocommerce.product.attribute", "export_batch", "root.woocommerce_export_batch"),
    (
        "woocommerce.product.attribute",
        "export_record",
        "root.woocommerce_export_record",
    ),
    (
        "woocommerce.product.attribute.value",
        "export_batch",
        "root.woocommerce_export_batch",
    ),
    (
        "woocommerce.product.attribute.value",
        "export_record",
        "root.woocommerce_export_record",
    ),
    ("woocommerce.sale.order", "export_batch", "root.woocommerce_export_batch"),
    ("woocommerce.sale.order", "export_record", "root.woocommerce_export_record"),
    ("woocommerce.sale.order", "import_batch", "root.woocommerce_import_batch"),
    ("woocommerce.sale.order", "import_chunk", "root.woocommerce_import_chunk"),
    ("woocommerce.sale.order", "import_record", "root.woocommerce_import_record"),
]


class TestQueueJobFunctions(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template.write({"default_code": "WC-QUEUE", "taxes_id": [(5, 0, 0)]})

    def test_functions_route_jobs_with_the_retry_pattern(self):
        for model_name, method_name, channel in FUNCTIONS:
            delayable = self.env[model_name].with_delay()
            job = self._new_job(
                model_name, method_name, getattr(delayable, method_name)
            )
            self.assertEqual(job.channel, channel)
            self.assertEqual(job.job_function_id._parse_retry_pattern(), RETRY_PATTERN)

    def test_export_retries_follow_the_stages_and_stop_at_attempt_20(self):
        binding_model = self.env["woocommerce.product.template"]
        job_record = self._new_job(
            "woocommerce.product.template",
            "export_record",
            lambda: binding_model.with_delay().export_record(
                self.backend, self.template
            ),
        )
        job = Job.load(self.env, job_record.uuid)
        waits = (
            [range(5, 16)] * 4
            + [range(20, 41)] * 5
            + [range(45, 76)] * 5
            + [range(240, 361)] * 5
        )
        with self.backend.work_on("woocommerce.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            with patch.object(type(adapter), "_exec", return_value={}) as call:
                call.side_effect = RetryableJobError("Temporary HTTP failure")
                for attempt, wait in enumerate(waits, start=1):
                    with self.assertRaises(RetryableJobError):
                        job.perform()
                    self.assertEqual(job.retry, attempt)
                    self.assertIn(job._get_retry_seconds(), wait)
                with self.assertRaises(FailedJobError):
                    job.perform()
                self.assertEqual(job.retry, 20)
