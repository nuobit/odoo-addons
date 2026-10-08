# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import timedelta
from io import BytesIO

from freezegun import freeze_time
from PIL import Image

from odoo.tools import lazy_property

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

    @staticmethod
    def _image_data(color):
        stream = BytesIO()
        Image.new("RGB", (8, 8), color).save(stream, format="PNG")
        return base64.b64encode(stream.getvalue())

    def _create_gallery_image(self, **values):
        return self.env["product.image"].create(
            {"name": "Gallery image", "image_1920": self._image_data("red"), **values}
        )

    def _add_export_dependency(self, model_name, path):
        """Make the export date of a model depend on one more path until the
        end of the test, as a module that sends one more field does."""
        field = self.env[model_name]._fields["woocommerce_write_date"]
        depends = field.depends
        field.depends = depends + (path,)
        lazy_property.reset_all(self.registry)

        def restore():
            field.depends = depends
            lazy_property.reset_all(self.registry)

        self.addCleanup(restore)

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
        self._translate(template, "website_name", "Nombre en la tienda")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(template, "website_name", "Otro nombre en la tienda")
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

    def test_image_title_translation_marks_variants_whose_date_depends_on_it(self):
        # As a module that sends the titles of the gallery images with the product
        self._add_export_dependency(
            "product.product", "product_tmpl_id.product_template_image_ids.title"
        )
        template = self._create_variable_template()
        image = self._create_gallery_image(
            product_tmpl_id=template.id, title="Gallery image title"
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(image, "title", "Título de la imagen")
        self.assert_touched(template.product_variant_ids)

    def test_image_title_translation_marks_nothing_when_no_date_depends_on_it(self):
        template = self._create_variable_template()
        image = self._create_gallery_image(
            product_tmpl_id=template.id, title="Gallery image title"
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._translate(image, "title", "Título de la imagen")
        self.assert_untouched(template)
        self.assert_untouched(template.product_variant_ids)
