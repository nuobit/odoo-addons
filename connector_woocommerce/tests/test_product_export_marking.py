# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import timedelta
from io import BytesIO

from freezegun import freeze_time
from PIL import Image

from .common import WooCommerceCase


class TestProductExportMarking(WooCommerceCase):
    """A change to a field the export sends marks the products that carry it:
    a simple product is exported as its template, a variable one through its
    variations."""

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

    @staticmethod
    def _variant(template, value_name):
        return template.product_variant_ids.filtered(
            lambda v: v.product_template_attribute_value_ids.name == value_name
        )

    # Simple products

    def test_website_name_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.website_name = "Product name on the shop"
        self.assert_touched(template)

    def test_short_description_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.public_short_description = "Short description on the shop"
        self.assert_touched(template)

    def test_slug_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.slug_name = "product-on-the-shop"
        self.assert_touched(template)

    def test_variant_description_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.product_variant_id.variant_public_description = "Variant description"
        self.assert_touched(template)

    def test_upsell_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.alternative_product_ids = self.unbound_template
        self.assert_touched(template)

    def test_cross_sell_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.accessory_product_ids = self.unbound_template.product_variant_id
        self.assert_touched(template)

    def test_type_change_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.type = "service"
        self.assert_touched(template)

    def test_gallery_image_added_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        self._create_gallery_image(product_tmpl_id=template.id)
        self.assert_touched(template)

    def test_gallery_image_removed_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        image = self._create_gallery_image(product_tmpl_id=template.id)
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        image.unlink()
        self.assert_touched(template)

    def test_gallery_reordered_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        image = self._create_gallery_image(product_tmpl_id=template.id)
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        image.sequence = 20
        self.assert_touched(template)

    def test_internal_notes_change_leaves_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self.clock.tick(timedelta(seconds=1))
        template.description = "Internal notes"
        self.assert_untouched(template)

    # Variable products

    def test_name_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.name = "Renamed variable product"
        self.assert_touched(template.product_variant_ids)

    def test_website_name_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.website_name = "Product name on the shop"
        self.assert_touched(template.product_variant_ids)

    def test_description_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.public_description = "Description on the shop"
        self.assert_touched(template.product_variant_ids)

    def test_short_description_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.public_short_description = "Short description on the shop"
        self.assert_touched(template.product_variant_ids)

    def test_slug_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.slug_name = "product-on-the-shop"
        self.assert_touched(template.product_variant_ids)

    def test_category_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.public_categ_ids = self.env["product.public.category"].create(
            {
                "name": "WooCommerce shop category",
                "slug_name": "woocommerce-shop-category",
            }
        )
        self.assert_touched(template.product_variant_ids)

    def test_template_gallery_image_added_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._create_gallery_image(product_tmpl_id=template.id)
        self.assert_touched(template.product_variant_ids)

    def test_template_gallery_reordered_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        image = self._create_gallery_image(product_tmpl_id=template.id)
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        image.sequence = 20
        self.assert_touched(template.product_variant_ids)

    def test_variant_gallery_image_added_marks_its_variant(self):
        template = self._create_variable_template()
        large = self._variant(template, "Large")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._create_gallery_image(product_variant_id=large.id)
        self.assert_touched(large)

    def test_variant_gallery_reordered_marks_its_variant(self):
        template = self._create_variable_template()
        large = self._variant(template, "Large")
        image = self._create_gallery_image(product_variant_id=large.id)
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        image.sequence = 20
        self.assert_touched(large)

    def test_archiving_one_variant_marks_it(self):
        template = self._create_variable_template()
        large = self._variant(template, "Large")
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        large.active = False
        self.assert_touched(large)
