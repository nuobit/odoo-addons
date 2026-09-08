# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from .common import WooCommerceCase


class TestExportSince(WooCommerceCase):
    def _new_export_batch_job(self, model_name, run):
        job_model = self.env["queue.job"]
        domain = [("model_name", "=", model_name), ("method_name", "=", "export_batch")]
        before = job_model.search(domain)
        run()
        jobs = job_model.search(domain) - before
        self.assertEqual(len(jobs), 1)
        return jobs

    def test_export_product_tmpl_since_keeps_base_domain(self):
        self.backend.export_product_tmpl_since_date = datetime(2026, 1, 1)
        job = self._new_export_batch_job(
            "woocommerce.product.template", self.backend.export_product_tmpl_since
        )
        domain = [list(clause) for clause in job.kwargs["domain"]]
        self.assertIn(["woocommerce_enabled", "=", True], domain)
        self.assertIn(["has_attributes", "=", False], domain)
        self.assertIn(["woocommerce_write_date", ">", "2026-01-01 00:00:00"], domain)

    def test_export_product_tmpl_without_since_date_uses_base_domain(self):
        job = self._new_export_batch_job(
            "woocommerce.product.template", self.backend.export_product_tmpl_since
        )
        domain = [list(clause) for clause in job.kwargs["domain"]]
        self.assertEqual(
            domain, [["woocommerce_enabled", "=", True], ["has_attributes", "=", False]]
        )
