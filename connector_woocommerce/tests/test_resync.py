# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.connector_extension_woocommerce.components.adapter import (
    ConnectorExtensionWooCommerceAdapterCRUD,
)
from odoo.addons.queue_job.job import Job

from .common import WooCommerceCase, WooCommerceOrderCase


class TestResyncExport(WooCommerceCase):
    def setUp(self):
        super().setUp()
        self.variable_template = self._create_variable_template()
        for index, value in enumerate(
            self.variable_template.attribute_line_ids.value_ids
        ):
            self.env["woocommerce.product.attribute.value"].create(
                {
                    "odoo_id": value.id,
                    "backend_id": self.backend.id,
                    "woocommerce_idattribute": 3001,
                    "woocommerce_idattributevalue": 4001 + index,
                }
            )
        self.binding = self.variable_template.woocommerce_bind_ids

    def _bind_variants(self):
        for index, variant in enumerate(self.variable_template.product_variant_ids):
            variant.default_code = "WC-RESYNC-%d" % (2001 + index)
            self.env["woocommerce.product.product"].create(
                {
                    **self._variant_binding_values(variant, 2001 + index),
                    "woocommerce_idparent": 1003,
                }
            )

    def _shop_calls(self, job_record):
        with patch.object(
            ConnectorExtensionWooCommerceAdapterCRUD, "_exec", return_value={}
        ) as woo:
            Job.load(self.env, job_record.uuid).perform()
        return [args for args, _kwargs in woo.call_args_list]

    def test_resync_queues_the_export_without_calling_the_shop(self):
        with patch.object(
            ConnectorExtensionWooCommerceAdapterCRUD, "_exec", return_value={}
        ) as woo:
            job = self._new_job(
                "woocommerce.product.template",
                "export_record",
                self.binding.resync_export,
            )
        woo.assert_not_called()
        self.assertEqual(job.args[1], self.variable_template)

    def test_resync_of_a_template_queues_no_job_for_its_variants(self):
        self._bind_variants()
        jobs = self._new_jobs(
            "woocommerce.product.product", "export_record", self.binding.resync_export
        )
        self.assertFalse(jobs)

    def test_queued_resync_of_a_template_sends_its_variants_and_attributes_once(self):
        self._bind_variants()
        job = self._new_job(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        calls = self._shop_calls(job)
        self.assertIn(("put", "products/1003/variations/2001"), calls)
        self.assertIn(("put", "products/1003/variations/2002"), calls)
        self.assertEqual(calls.count(("put", "products/attributes/3001")), 1)

    def test_resync_while_the_first_one_waits_queues_nothing(self):
        self._new_job(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        jobs = self._new_jobs(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        self.assertFalse(jobs)

    def test_resync_after_the_first_one_started_queues_a_new_job(self):
        job = self._new_job(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        started = Job.load(self.env, job.uuid)
        started.set_started()
        started.store()
        jobs = self._new_jobs(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        self.assertEqual(len(jobs), 1)

    def test_queued_resync_sends_the_bound_attributes_again(self):
        job = self._new_job(
            "woocommerce.product.template", "export_record", self.binding.resync_export
        )
        calls = self._shop_calls(job)
        self.assertIn(("put", "products/attributes/3001"), calls)
        self.assertIn(("put", "products/attributes/3001/terms/4001"), calls)
        self.assertIn(("put", "products/attributes/3001/terms/4002"), calls)

    def test_ordinary_export_leaves_the_bound_attributes_alone(self):
        binding_model = self.env["woocommerce.product.template"]
        job = self._new_job(
            "woocommerce.product.template",
            "export_record",
            lambda: binding_model.with_delay().export_record(
                self.backend, self.variable_template
            ),
        )
        calls = self._shop_calls(job)
        self.assertNotIn(("put", "products/attributes/3001"), calls)
        self.assertNotIn(("put", "products/attributes/3001/terms/4001"), calls)
        self.assertNotIn(("put", "products/attributes/3001/terms/4002"), calls)


class TestResyncImport(WooCommerceOrderCase):
    def test_resync_import_queues_the_import_without_calling_the_shop(self):
        binding = self._bind_order(self._create_order({self.product_1: 1}), 5001)
        with patch.object(
            ConnectorExtensionWooCommerceAdapterCRUD, "_exec", return_value={}
        ) as woo:
            job = self._new_job(
                "woocommerce.sale.order", "import_record", binding.resync_import
            )
        woo.assert_not_called()
        self.assertEqual(job.args[0], self.backend)
        self.assertEqual(job.args[1], [5001])

    def test_queued_resync_import_runs_the_importer_on_the_order(self):
        binding = self._bind_order(self._create_order({self.product_1: 1}), 5001)
        job = self._new_job(
            "woocommerce.sale.order", "import_record", binding.resync_import
        )
        with self.backend.work_on("woocommerce.sale.order") as work:
            importer = work.component(usage="record.direct.importer")
        with patch.object(type(importer), "run") as run:
            Job.load(self.env, job.uuid).perform()
        run.assert_called_once_with([5001], job.args[2], external_data={})
