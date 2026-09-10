# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestExportSince(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_template = cls._create_template("Second bound product", 1002)
        cls.variable_template = cls._create_template("Variable product", 1003)
        attribute = cls.env["product.attribute"].create({"name": "Size"})
        values = cls.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        cls.variable_template.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    )
                ]
            }
        )
        for index, variant in enumerate(cls.variable_template.product_variant_ids):
            cls._bind_variant(variant, 2001 + index)

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _start_incremental_exports(self):
        self.clock.tick(timedelta(seconds=1))
        self.backend.export_product_tmpl_since()
        self.backend.export_products_since()
        self._remember_write_dates(
            self.template | self.second_template | self.variable_template
        )

    def _assert_selected(self, model_name, action, expected):
        job = self._new_export_batch_job(model_name, action)
        selected = (
            self.env[expected._name]
            .with_context(active_test=False)
            .search(job.kwargs["domain"])
        )
        self.assertEqual(selected.sorted("id"), expected.sorted("id"))
        return job

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
        self.assertIn(["woocommerce_write_date", ">=", "2026-01-01 00:00:00"], domain)

    def test_export_product_tmpl_without_since_date_uses_base_domain(self):
        job = self._new_export_batch_job(
            "woocommerce.product.template", self.backend.export_product_tmpl_since
        )
        domain = [list(clause) for clause in job.kwargs["domain"]]
        self.assertEqual(
            domain, [["woocommerce_enabled", "=", True], ["has_attributes", "=", False]]
        )

    def test_edit_in_same_second_as_previous_export_is_selected(self):
        rule = self._create_rule()
        self._start_incremental_exports()
        rule.fixed_price = 75.0
        self.assertEqual(
            self.template.woocommerce_write_date,
            self.backend.export_product_tmpl_since_date,
        )
        self.clock.tick(timedelta(seconds=1))
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
