# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestAttributeCategoryTranslationMarking(WooCommerceCase):
    """A translation saved on its own, as the translation dialog does, moves
    the export date of the attribute value, attribute or category it
    translates."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("es_ES")

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

    def test_new_translation_marks_attribute_value(self):
        self._translate(self.value, "name", "Talla única")
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_changed_translation_marks_attribute_value(self):
        self._translate(self.value, "name", "Talla única")
        self.clock.tick(timedelta(seconds=1))
        self._translate(self.value, "name", "Única")
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 2)
        )

    def test_removed_translation_marks_attribute_value(self):
        translation = self._translate(self.value, "name", "Talla única")
        self.clock.tick(timedelta(seconds=1))
        translation.unlink()
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 2)
        )

    def test_untranslated_attribute_value_keeps_its_export_date(self):
        other_value = self.env["product.attribute.value"].create(
            {"name": "Large", "attribute_id": self.attribute.id}
        )
        self._translate(other_value, "name", "Grande")
        self.assertEqual(
            self.value.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )

    def test_new_translation_marks_attribute(self):
        self._translate(self.attribute, "name", "Talla")
        self.assertEqual(
            self.attribute.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_new_translation_marks_category(self):
        self._translate(self.category, "name", "Mascarillas")
        self.assertEqual(
            self.category.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_translation_of_deleted_attribute_value_can_be_changed(self):
        value = self.env["product.attribute.value"].create(
            {"name": "Large", "attribute_id": self.attribute.id}
        )
        translation = self._translate(value, "name", "Grande")
        value.unlink()
        # A record rule reads the records it checks, a deleted one too.
        self.env["ir.rule"].create(
            {
                "name": "Named attribute values",
                "model_id": self.env.ref("product.model_product_attribute_value").id,
                "domain_force": "[('name', '!=', False)]",
            }
        )
        # Without its record, the translation is changed from the list of
        # translated terms.
        translation.with_user(self.env.ref("base.user_admin")).value = "Grande XL"
        self.assertEqual(translation.value, "Grande XL")
