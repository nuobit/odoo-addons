# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.job import Job

from .common import WooCommerceCase


class TestWooCommerceSale(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template.write({"default_code": "WC-SALE", "taxes_id": [(5, 0, 0)]})
        cls.variant = cls.template.product_variant_id
        cls._bind_variant(cls.variant, 2001)

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _product_exports(self):
        return (
            ("woocommerce.product.template", self.template, [1001]),
            ("woocommerce.product.product", self.variant, [1001, 2001]),
        )

    def _export_payload(self, model_name, product, external_id):
        with self.backend.work_on(model_name) as work:
            mapper = work.component(usage="export.mapper")
            # The exporter maps the actual product, not its binding.
            data = mapper.map_record(product).values()
            adapter = work.component(usage="backend.adapter")
            # Stop only at the external API boundary; run real formatting.
            with patch.object(type(adapter), "_exec", return_value={}) as call:
                adapter.write(external_id, data)
            call.assert_called_once()
            args, kwargs = call.call_args
            self.assertEqual(args[0], "put")
            return kwargs["data"]

    def _assert_sale_payload(self, price):
        for model_name, product, external_id in self._product_exports():
            with self.subTest(model=model_name):
                payload = self._export_payload(model_name, product, external_id)
                self.assertEqual(payload["sale_price"], price)
                self.assertEqual(payload["date_on_sale_from_gmt"], "")
                self.assertEqual(payload["date_on_sale_to_gmt"], "")

    def _assert_price_payload(self, regular, sale):
        for model_name, product, external_id in self._product_exports():
            with self.subTest(model=model_name):
                payload = self._export_payload(model_name, product, external_id)
                self.assertEqual(payload["regular_price"], regular)
                self.assertEqual(payload["sale_price"], sale)

    def _create_variable_template(self):
        attribute = self.env["product.attribute"].create({"name": "Size"})
        values = self.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        self.env["woocommerce.product.attribute"].create(
            {
                "odoo_id": attribute.id,
                "backend_id": self.backend.id,
                "woocommerce_idattribute": 3001,
            }
        )
        template = self._create_template("Variable product", 1003)
        template.write(
            {
                "taxes_id": [(5, 0, 0)],
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    ),
                ],
            }
        )
        return template

    def test_current_sale_keeps_woocommerce_dates_empty(self):
        self._create_rule(
            date_start="2029-12-20 08:30:00", date_end="2030-01-10 19:45:00"
        )
        self.backend = self.backend.with_context(tz="Pacific/Honolulu")
        self._assert_sale_payload("80.0")

    def test_expired_sale_clears_price_and_dates(self):
        self._create_rule(
            date_start="2029-12-01 00:00:00", date_end="2029-12-31 23:59:59"
        )
        self._assert_sale_payload("")

    def test_future_sale_clears_price_and_dates(self):
        self._create_rule(
            fixed_price=70.0,
            date_start="2030-01-10 08:30:00",
            date_end="2030-01-20 19:45:00",
        )
        self._assert_sale_payload("")

    def test_undated_sale_clears_previous_schedule(self):
        self._create_rule()
        self._assert_sale_payload("80.0")

    def test_missing_rule_clears_remote_sale(self):
        self._assert_sale_payload("")

    def test_missing_discount_pricelist_clears_remote_sale(self):
        self.backend.discount_pricelist_id = False
        self._assert_sale_payload("")

    def test_price_at_or_above_regular_is_exported_as_is(self):
        # Whether a rule price is an offer is WooCommerce's decision, not ours.
        rule = self._create_rule(fixed_price=100.0)
        for price, exported in ((100.0, "100.0"), (120.0, "120.0")):
            with self.subTest(price=price):
                rule.fixed_price = price
                self._assert_sale_payload(exported)

    def test_zero_price_is_exported_as_a_sale(self):
        self._create_rule(fixed_price=0.0)
        self._assert_sale_payload("0.0")

    def test_list_price_is_exported_as_text(self):
        self._create_rule()
        self._assert_price_payload("100.0", "80.0")

    def test_zero_list_price_is_exported_as_no_price(self):
        self._create_rule()
        self.template.list_price = 0.0
        self._assert_price_payload("", "80.0")

    def test_negative_prices_are_exported_as_is(self):
        # Neither end rejects a negative price: a wrong sign is corrected in
        # Odoo and re-synchronized, never filtered here.
        self._create_rule(fixed_price=-10.0)
        self.template.list_price = -5.0
        self._assert_price_payload("-5.0", "-10.0")

    def test_variable_product_sends_no_price_keys(self):
        # The parent's prices live on its variants: sending no key at all is
        # what leaves them untouched on WooCommerce.
        payload = self._export_payload(
            "woocommerce.product.template", self._create_variable_template(), [1003]
        )
        for key in (
            "regular_price",
            "sale_price",
            "date_on_sale_from_gmt",
            "date_on_sale_to_gmt",
        ):
            self.assertNotIn(key, payload)

    def test_one_unit_uses_current_price_instead_of_bulk_or_future_price(self):
        self._create_rule(fixed_price=80.0)
        self._create_rule(fixed_price=50.0, min_quantity=10.0)
        self._create_rule(fixed_price=70.0, date_start="2030-01-10 00:00:00")
        self._assert_sale_payload("80.0")

    def test_current_category_rule_matches_ancestors_only(self):
        parent = self.env["product.category"].create({"name": "Parent category"})
        other = self.env["product.category"].create({"name": "Unrelated category"})
        self.category.parent_id = parent
        self._create_rule(
            applied_on="2_product_category",
            product_tmpl_id=False,
            categ_id=other.id,
            fixed_price=50.0,
            date_start="2030-01-01 00:00:00",
        )
        self._create_rule(
            applied_on="2_product_category",
            product_tmpl_id=False,
            categ_id=parent.id,
            date_start="2030-01-01 00:00:00",
        )
        self._assert_sale_payload("80.0")

    def test_current_rule_uses_pricelist_precedence(self):
        self._create_rule(
            applied_on="3_global",
            product_tmpl_id=False,
            fixed_price=50.0,
            date_start="2030-01-01 00:00:00",
            date_end="2030-01-20 00:00:00",
        )
        self._create_rule(
            applied_on="0_product_variant",
            product_tmpl_id=False,
            product_id=self.variant.id,
            fixed_price=90.0,
            date_start="2030-01-01 00:00:00",
            date_end="2030-01-15 00:00:00",
        )
        self._assert_sale_payload("90.0")

    def test_current_percentage_uses_standard_pricelist_calculation(self):
        self._create_rule(
            compute_price="percentage",
            percent_price=25.0,
            date_start="2030-01-01 00:00:00",
        )
        self._assert_sale_payload("75.0")

    def test_current_formula_uses_base_pricelist(self):
        self._create_rule(pricelist=self.other_pricelist, fixed_price=80.0)
        self._create_rule(
            compute_price="formula",
            base="pricelist",
            base_pricelist_id=self.other_pricelist.id,
            price_discount=10.0,
            date_start="2030-01-01 00:00:00",
        )
        self._assert_sale_payload("72.0")

    def test_current_sale_is_kept_ahead_of_a_later_offer(self):
        self._create_rule(date_end="2030-01-05 00:00:00")
        self._create_rule(fixed_price=70.0, date_start="2030-01-10 00:00:00")
        self._assert_sale_payload("80.0")

    def test_validity_end_is_inclusive_and_then_clears_the_sale(self):
        self._create_rule(
            date_start="2030-01-01 12:00:00", date_end="2030-01-01 12:00:00"
        )
        self._assert_sale_payload("80.0")
        with freeze_time("2030-01-01 12:00:01"):
            self._assert_sale_payload("")

    def test_archived_product_uses_its_archived_variant(self):
        self._create_rule()
        self.template.action_archive()
        self._assert_sale_payload("80.0")

    def _queue_incremental_template_export(self):
        job_model = self.env["queue.job"]
        previous_jobs = job_model.search([])
        self.backend.export_product_tmpl_since()
        batch = job_model.search([]) - previous_jobs
        self.assertEqual(len(batch), 1)
        Job.load(self.env, batch.uuid).perform()
        record_job = job_model.search([]) - previous_jobs - batch
        self.assertEqual(len(record_job), 1)
        self.assertEqual(record_job.method_name, "export_record")
        self.assertEqual(record_job.args[1], self.template)
        return Job.load(self.env, record_job.uuid)

    def test_queued_export_retry_recalculates_current_price(self):
        self._create_rule(date_end="2030-01-02 00:00:00")
        self.backend.export_product_tmpl_since_date = "2030-01-01 12:00:00"
        job = self._queue_incremental_template_export()
        with self.backend.work_on("woocommerce.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            with patch.object(type(adapter), "_exec", return_value={}) as call:
                call.side_effect = RetryableJobError("Temporary HTTP failure")
                with self.assertRaises(RetryableJobError):
                    job.perform()
                self.assertEqual(call.call_args[1]["data"]["sale_price"], "80.0")
                self.clock.move_to("2030-01-03 00:00:00")
                call.side_effect = None
                job.perform()
                self.assertEqual(call.call_count, 2)
                payload = call.call_args[1]["data"]
                self.assertEqual(payload["sale_price"], "")
                self.assertEqual(payload["date_on_sale_from_gmt"], "")
                self.assertEqual(payload["date_on_sale_to_gmt"], "")

    def test_pricelist_create_edit_delete_reaches_incremental_export_payload(self):
        self.backend.export_product_tmpl_since_date = "2030-01-01 12:00:00"
        rule = self._create_rule()
        with self.backend.work_on("woocommerce.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            with patch.object(type(adapter), "_exec", return_value={}) as call:
                for change, expected_price in (
                    (None, "80.0"),
                    ({"fixed_price": 75.0}, "75.0"),
                    ("delete", ""),
                ):
                    with self.subTest(change=change):
                        self.clock.tick(timedelta(seconds=1))
                        if change == "delete":
                            rule.unlink()
                        elif change:
                            rule.write(change)
                        self._queue_incremental_template_export().perform()
                        call.assert_called_once()
                        payload = call.call_args[1]["data"]
                        self.assertEqual(payload["sale_price"], expected_price)
                        self.assertEqual(payload["date_on_sale_from_gmt"], "")
                        self.assertEqual(payload["date_on_sale_to_gmt"], "")
                        call.reset_mock()
