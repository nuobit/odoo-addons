# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestProductTranslationMarking(WooCommerceCase):
    """A translation saved on its own, as the translation dialog does, marks
    the products that carry the translated field."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("es_ES")

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _translate(self, record, field_name, value):
        return self.env["ir.translation"].create(
            {
                "type": "model",
                "name": "%s,%s" % (record._name, field_name),
                "res_id": record.id,
                "lang": "es_ES",
                "src": record[field_name],
                "value": value,
                "state": "translated",
            }
        )

    def test_new_translation_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        template.website_name = "Product name on the shop"
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(template, "website_name", "Nombre en la tienda")
        self.assert_touched(template)

    def test_changed_translation_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        template.website_name = "Product name on the shop"
        translation = self._translate(template, "website_name", "Nombre en la tienda")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        translation.value = "Otro nombre en la tienda"
        self.assert_touched(template)

    def test_removed_translation_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        template.website_name = "Product name on the shop"
        translation = self._translate(template, "website_name", "Nombre en la tienda")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        translation.unlink()
        self.assert_touched(template)

    def test_template_translation_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        template.website_name = "Product name on the shop"
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(template, "website_name", "Nombre en la tienda")
        self.assert_touched(template.product_variant_ids)

    def test_variant_translation_marks_its_variant(self):
        template = self._create_variable_template()
        variant = template.product_variant_ids[0]
        variant.variant_public_description = "Variant description"
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(variant, "variant_public_description", "Descripción")
        self.assert_touched(variant)
