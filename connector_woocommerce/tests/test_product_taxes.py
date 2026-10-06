# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestProductTaxes(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {"name": "WooCommerce reduced tax", "amount": 10.0, "type_tax_use": "sale"}
        )
        cls.other_tax = cls.env["account.tax"].create(
            {"name": "WooCommerce general tax", "amount": 21.0, "type_tax_use": "sale"}
        )

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _map_tax(self, tax, woocommerce_tax_class):
        return self.env["woocommerce.backend.tax.class"].create(
            {
                "backend_id": self.backend.id,
                "account_tax_id": tax.id,
                "woocommerce_tax_class": woocommerce_tax_class,
            }
        )

    def test_tax_change_marks_simple_template(self):
        self.template.taxes_id = self.tax
        self.assert_touched(self.template)

    def test_tax_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.taxes_id = self.tax
        self.assert_touched(template.product_variant_ids)

    def test_tax_class_change_marks_simple_template(self):
        template = self._create_template("WooCommerce taxed product")
        template.taxes_id = self.tax
        tax_class = self._map_tax(self.tax, "standard")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.woocommerce_tax_class = "reduced-rate"
        self.assert_touched(template)

    def test_tax_class_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        template.taxes_id = self.tax
        tax_class = self._map_tax(self.tax, "standard")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.woocommerce_tax_class = "reduced-rate"
        self.assert_touched(template.product_variant_ids)

    def test_new_tax_class_marks_the_products_of_its_tax(self):
        template = self._create_template("WooCommerce taxed product")
        template.taxes_id = self.tax
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._map_tax(self.tax, "reduced-rate")
        self.assert_touched(template)

    def test_removed_tax_class_marks_the_products_of_its_tax(self):
        template = self._create_template("WooCommerce taxed product")
        template.taxes_id = self.tax
        tax_class = self._map_tax(self.tax, "reduced-rate")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.unlink()
        self.assert_touched(template)

    def test_tax_class_moved_to_another_tax_marks_the_products_of_both(self):
        template = self._create_template("WooCommerce taxed product")
        other_template = self._create_template("WooCommerce other product")
        template.taxes_id = self.tax
        other_template.taxes_id = self.other_tax
        tax_class = self._map_tax(self.tax, "reduced-rate")
        self._remember_write_dates(template)
        self._remember_write_dates(other_template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.account_tax_id = self.other_tax
        self.assert_touched(template | other_template)

    def test_tax_class_moved_to_another_backend_marks_the_products_of_its_tax(self):
        other_backend = self.backend.copy()
        template = self._create_template("WooCommerce taxed product")
        template.taxes_id = self.tax
        tax_class = self._map_tax(self.tax, "reduced-rate")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.backend_id = other_backend
        self.assert_touched(template)

    def test_tax_class_change_leaves_the_products_of_other_taxes(self):
        template = self._create_template("WooCommerce taxed product")
        template.taxes_id = self.other_tax
        tax_class = self._map_tax(self.tax, "standard")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        tax_class.woocommerce_tax_class = "reduced-rate"
        self.assert_untouched(template)
