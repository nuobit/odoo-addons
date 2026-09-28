# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from odoo.addons.connector_extension_woocommerce.components.adapter import (
    ConnectorExtensionWooCommerceAdapterCRUD,
)

from .common import WooCommerceCase


class TestExportMapperImages(WooCommerceCase):
    def setUp(self):
        super().setUp()
        self.media_backend = self.env["wordpress.backend"].create(
            {
                "name": "WordPress image test backend",
                "url": "http://127.0.0.1:1",
                "username": "odoo.test",
                "application_password": "test",
                "lang_ids": [(6, 0, self.langs.ids)],
            }
        )
        self.backend.wordpress_backend_id = self.media_backend
        self.template = self._create_variable_template()
        self.template.image_1920 = self._image_data("white")
        self.variant = self.template.product_variant_ids[0]
        self.variant.default_code = "WC-IMAGES"

    @staticmethod
    def _image_data(color):
        stream = BytesIO()
        Image.new("RGB", (8, 8), color).save(stream, format="PNG")
        return base64.b64encode(stream.getvalue())

    def _bind_image(self, record, field, external_id):
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("res_field", "=", field),
            ]
        )
        self.assertEqual(len(attachment), 1)
        self.env["wordpress.ir.attachment"].create(
            {
                "odoo_id": attachment.id,
                "backend_id": self.media_backend.id,
                "wordpress_idattachment": external_id,
                "wordpress_source_url": "https://shop.example.test/image-%s.png"
                % external_id,
            }
        )

    def _create_extra_image(self, external_id, sequence, color):
        image = self.env["product.image"].create(
            {
                "name": "Extra image %s" % external_id,
                "product_variant_id": self.variant.id,
                "sequence": sequence,
                "image_1920": self._image_data(color),
            }
        )
        self._bind_image(image, "image_1920", external_id)
        return image

    def test_variant_exports_all_images_in_sequence(self):
        self.backend.use_main_product_variant_image = "no"
        self._create_extra_image(202, 20, "green")
        self._create_extra_image(201, 10, "red")
        self._create_extra_image(203, 30, "blue")

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 201})
        self.assertEqual(values["gallery_image_ids"], [202, 203])

    def test_variant_main_image_first(self):
        self.backend.use_main_product_image = "no"
        self.backend.use_main_product_variant_image = "first"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)
        self._create_extra_image(202, 10, "green")
        self._create_extra_image(203, 20, "blue")

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 201})
        self.assertEqual(values["gallery_image_ids"], [202, 203])

    def test_variant_main_image_last(self):
        self.backend.use_main_product_image = "first"
        self.backend.use_main_product_variant_image = "last"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)
        self._create_extra_image(202, 10, "green")
        self._create_extra_image(203, 20, "blue")

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 202})
        self.assertEqual(values["gallery_image_ids"], [203, 201])

    def test_variant_excludes_main_image(self):
        self.backend.use_main_product_image = "first"
        self.backend.use_main_product_variant_image = "no"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)
        self._create_extra_image(202, 10, "green")
        self._create_extra_image(203, 20, "blue")

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 202})
        self.assertEqual(values["gallery_image_ids"], [203])

    def test_variant_single_image_clears_old_gallery(self):
        self.backend.use_main_product_image = "no"
        self.backend.use_main_product_variant_image = "first"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 201})
        self.assertEqual(values["gallery_image_ids"], [])

    def test_variant_without_images_clears_old_gallery(self):
        self.backend.use_main_product_variant_image = "first"

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {})
        self.assertEqual(values["gallery_image_ids"], [])

    def test_variant_excluded_main_without_extras_clears_images(self):
        self.backend.use_main_product_image = "first"
        self.backend.use_main_product_variant_image = "no"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {})
        self.assertEqual(values["gallery_image_ids"], [])

    def test_test_database_missing_image_keeps_remote_images(self):
        self.backend.use_main_product_variant_image = "first"
        self.media_backend.test_database = True
        self.variant.image_1920 = self._image_data("red")

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertNotIn("image", values)
        self.assertNotIn("gallery_image_ids", values)

    def test_variant_last_exports_sole_main_image(self):
        self.backend.use_main_product_image = "no"
        self.backend.use_main_product_variant_image = "last"
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)

        values = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(values["image"], {"id": 201})
        self.assertEqual(values["gallery_image_ids"], [])

    def test_template_excludes_main_when_variant_uses_first(self):
        self.backend.use_main_product_image = "no"
        self.backend.use_main_product_variant_image = "first"
        self._bind_image(self.template, "image_1920", 101)
        extra = self.env["product.image"].create(
            {
                "name": "Template extra",
                "product_tmpl_id": self.template.id,
                "sequence": 10,
                "image_1920": self._image_data("green"),
            }
        )
        self._bind_image(extra, "image_1920", 102)

        values = self._mapped_values("woocommerce.product.template", self.template)

        self.assertEqual(values["images"], [{"id": 102}])

    def test_template_keeps_main_when_variant_uses_no(self):
        self.backend.use_main_product_image = "first"
        self.backend.use_main_product_variant_image = "no"
        self._bind_image(self.template, "image_1920", 101)

        values = self._mapped_values("woocommerce.product.template", self.template)

        self.assertEqual(values["images"], [{"id": 101}])

    def test_variant_image_list_follows_each_policy_context(self):
        self.variant.image_1920 = self._image_data("red")
        self._bind_image(self.variant, "image_variant_1920", 201)
        self._create_extra_image(202, 10, "green")

        self.backend.use_main_product_variant_image = "first"
        first = self._mapped_values("woocommerce.product.product", self.variant)
        self.backend.use_main_product_variant_image = "no"
        excluded = self._mapped_values("woocommerce.product.product", self.variant)
        self.backend.use_main_product_variant_image = "last"
        last = self._mapped_values("woocommerce.product.product", self.variant)

        self.assertEqual(first["image"], {"id": 201})
        self.assertEqual(first["gallery_image_ids"], [202])
        self.assertEqual(excluded["image"], {"id": 202})
        self.assertEqual(excluded["gallery_image_ids"], [])
        self.assertEqual(last["image"], {"id": 202})
        self.assertEqual(last["gallery_image_ids"], [201])

    def test_template_image_list_follows_each_policy_context(self):
        self._bind_image(self.template, "image_1920", 101)
        extra = self.env["product.image"].create(
            {
                "name": "Template extra",
                "product_tmpl_id": self.template.id,
                "sequence": 10,
                "image_1920": self._image_data("green"),
            }
        )
        self._bind_image(extra, "image_1920", 102)

        self.backend.use_main_product_image = "first"
        first = self._mapped_values("woocommerce.product.template", self.template)
        self.backend.use_main_product_image = "no"
        excluded = self._mapped_values("woocommerce.product.template", self.template)
        self.backend.use_main_product_image = "last"
        last = self._mapped_values("woocommerce.product.template", self.template)

        self.assertEqual(first["images"], [{"id": 101}, {"id": 102}])
        self.assertEqual(excluded["images"], [{"id": 102}])
        self.assertEqual(last["images"], [{"id": 102}, {"id": 101}])

    def test_missing_image_binding_blocks_normal_export(self):
        self.backend.use_main_product_variant_image = "first"
        self.media_backend.test_database = False
        self.variant.image_1920 = self._image_data("red")

        with self.assertRaises(AssertionError):
            self._mapped_values("woocommerce.product.product", self.variant)

    def test_export_uploads_all_images_for_one_active_variant(self):
        self.backend.use_main_product_image = "no"
        self.backend.use_main_product_variant_image = "first"
        self.media_backend.test_database = False
        self.variant.image_1920 = self._image_data("red")
        (self.template.product_variant_ids - self.variant).action_archive()
        self.assertTrue(self.template.has_attributes)
        self.assertEqual(len(self.template.product_variant_ids), 1)
        self.env["product.image"].create(
            {
                "name": "Green extra",
                "product_variant_id": self.variant.id,
                "sequence": 10,
                "image_1920": self._image_data("green"),
            }
        )
        self.env["product.image"].create(
            {
                "name": "Blue extra",
                "product_variant_id": self.variant.id,
                "sequence": 20,
                "image_1920": self._image_data("blue"),
            }
        )
        for index, value in enumerate(self.template.attribute_line_ids.value_ids):
            self.env["woocommerce.product.attribute.value"].create(
                {
                    "odoo_id": value.id,
                    "backend_id": self.backend.id,
                    "woocommerce_idattribute": 3001,
                    "woocommerce_idattributevalue": 4001 + index,
                }
            )
        binding = self.env["woocommerce.product.product"].create(
            {
                "odoo_id": self.variant.id,
                "backend_id": self.backend.id,
                "woocommerce_idproduct": 2001,
                "woocommerce_idparent": 1003,
            }
        )
        with self.media_backend.work_on("wordpress.ir.attachment") as work:
            media_adapter = work.component(usage="backend.adapter")
        responses = [
            {"id": 201, "source_url": "https://shop.example.test/red.png"},
            {"id": 202, "source_url": "https://shop.example.test/green.png"},
            {"id": 203, "source_url": "https://shop.example.test/blue.png"},
        ]
        with patch.object(
            type(media_adapter), "_exec", side_effect=responses
        ) as upload, patch.object(
            ConnectorExtensionWooCommerceAdapterCRUD, "_exec", return_value={}
        ) as woo:
            binding.resync_export()

        self.assertEqual(upload.call_count, 3)
        for args, _kwargs in upload.call_args_list:
            self.assertEqual(args, ("post", "media"))
        variant_calls = [
            kwargs
            for args, kwargs in woo.call_args_list
            if args == ("put", "products/1003/variations/2001")
        ]
        self.assertEqual(len(variant_calls), 1)
        self.assertEqual(variant_calls[0]["data"]["image"], {"id": 201})
        self.assertEqual(variant_calls[0]["data"]["gallery_image_ids"], [202, 203])
