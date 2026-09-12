# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.tests.common import SavepointComponentCase

from .common import WooCommerceCase


class TestExportSince(WooCommerceCase, SavepointComponentCase):
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

    def test_start_marks_product_without_any_rule_edit(self):
        rule = self._create_rule(date_start="2030-01-01 12:10:00")
        original_rule_write_date = rule.write_date
        self._start_incremental_exports()
        self.clock.move_to("2030-01-01 12:10:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assert_touched(self.template)
        self.assert_untouched(self.second_template)
        self.assertEqual(rule.write_date, original_rule_write_date)

    def test_end_is_detected_after_equality_not_before(self):
        self._create_rule(date_end="2030-01-01 12:10:00")
        self._start_incremental_exports()
        self.clock.move_to("2030-01-01 12:10:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.env["product.template"],
        )
        self.assert_untouched(self.template)
        self.clock.tick(timedelta(seconds=1))
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assert_touched(self.template)

    def test_missed_start_and_end_are_recovered_after_downtime(self):
        self._create_rule(
            date_start="2030-01-02 00:00:00", date_end="2030-01-03 00:00:00"
        )
        self._start_incremental_exports()
        self.clock.move_to("2030-01-05 00:00:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )

    def test_unrelated_future_and_bulk_rules_do_not_mark_products(self):
        self._create_rule(
            pricelist=self.other_pricelist, date_start="2030-01-02 00:00:00"
        )
        self._create_rule(date_start="2030-01-04 00:00:00")
        self._create_rule(min_quantity=10, date_start="2030-01-02 00:00:00")
        self._start_incremental_exports()
        self.clock.move_to("2030-01-03 00:00:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.env["product.template"],
        )
        self.assert_untouched(self.template | self.second_template)

    def test_variant_and_template_streams_cover_their_own_boundaries(self):
        variants = self.variable_template.product_variant_ids.sorted("id")
        archived_variant = variants[0]
        archived_variant.action_archive()
        self._create_rule(
            product_tmpl_id=self.variable_template.id, date_start="2030-01-02 00:00:00"
        )
        self._create_rule(date_start="2030-01-02 00:00:00")
        self._start_incremental_exports()
        self.clock.move_to("2030-01-02 00:00:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assert_untouched(variants)
        self._assert_selected(
            "woocommerce.product.product",
            self.backend.export_products_since,
            variants,
        )
        self.assert_touched(variants)

    def test_nested_base_pricelist_boundary_marks_product(self):
        third_list = self.env["product.pricelist"].create({"name": "Nested base list"})
        self._create_rule(pricelist=third_list, date_end="2030-01-02 00:00:00")
        for pricelist, base_list in (
            (self.discount_pricelist, self.other_pricelist),
            (self.other_pricelist, third_list),
        ):
            self._create_rule(
                pricelist=pricelist,
                compute_price="formula",
                base="pricelist",
                base_pricelist_id=base_list.id,
            )
        self._start_incremental_exports()
        self.clock.move_to("2030-01-03 00:00:00")
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )

    def test_failed_transaction_preserves_boundaries_for_retry(self):
        self._create_rule(date_start="2030-01-02 00:00:00")
        self._start_incremental_exports()
        previous_cursor = self.backend.export_product_tmpl_since_date
        previous_jobs = self.env["queue.job"].search([])
        self.clock.move_to("2030-01-02 00:00:00")
        with self.assertRaises(UserError), self.cr.savepoint():
            self._assert_selected(
                "woocommerce.product.template",
                self.backend.export_product_tmpl_since,
                self.template,
            )
            raise UserError(_("Abort this export transaction"))
        self.assertEqual(self.backend.export_product_tmpl_since_date, previous_cursor)
        self.assertEqual(self.env["queue.job"].search([]), previous_jobs)
        self.assert_untouched(self.template)
        self._assert_selected(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
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

    def test_changing_or_removing_backend_pricelist_marks_bound_products(self):
        self._start_incremental_exports()
        for pricelist in (self.other_pricelist, self.env["product.pricelist"]):
            self.clock.tick(timedelta(seconds=1))
            self.backend.discount_pricelist_id = pricelist
            self._assert_selected(
                "woocommerce.product.template",
                self.backend.export_product_tmpl_since,
                self.template | self.second_template,
            )
            self._assert_selected(
                "woocommerce.product.product",
                self.backend.export_products_since,
                self.variable_template.product_variant_ids,
            )
