# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestAttributeCategoryExportMarking(WooCommerceCase):
    """A change to a field the export sends moves the export date of the
    attribute, attribute value or category; a change to any other field
    leaves it."""

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)
        self.attribute = self.env["product.attribute"].create({"name": "Size"})
        self.value = self.env["product.attribute.value"].create(
            {"name": "One size", "attribute_id": self.attribute.id}
        )
        self.category = self.env["product.public.category"].create(
            {"name": "Masks", "slug_name": "masks"}
        )
        # The export dates are computed now, before the clock moves on.
        self.env["base"].flush()
        self.clock.tick(timedelta(seconds=1))

    # Attributes

    def test_name_change_marks_attribute(self):
        self.attribute.name = "Length"
        self.assertEqual(
            self.attribute.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_sequence_change_leaves_attribute(self):
        self.attribute.sequence = 5
        self.assertEqual(
            self.attribute.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )

    # Attribute values

    def test_name_change_marks_attribute_value(self):
        self.value.name = "Unique size"
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_sequence_change_leaves_attribute_value(self):
        self.value.sequence = 5
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )

    # Categories

    def test_name_change_marks_category(self):
        self.category.name = "Face masks"
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_description_change_marks_category(self):
        self.category.description = "Masks for every therapy"
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_slug_change_marks_category(self):
        self.category.slug_name = "face-masks"
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_parent_change_marks_category(self):
        self.category.parent_id = self.env["product.public.category"].create(
            {"name": "Therapy", "slug_name": "therapy"}
        )
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_sequence_change_leaves_category(self):
        self.category.sequence = 5
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )
