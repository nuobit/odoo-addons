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

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def test_tax_change_marks_simple_template(self):
        self.template.taxes_id = self.tax
        self.assert_touched(self.template)

    def test_tax_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.taxes_id = self.tax
        self.assert_touched(template.product_variant_ids)
