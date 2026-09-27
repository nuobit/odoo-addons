# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import PLACEHOLDER, TEXT, TEXT_HEX, WooCommerceCase

IMAGE = '<p><img src="x"></p>'


class TestExportMapperHtml(WooCommerceCase):
    """A visually empty text leaves the mapper as no value and clears WooCommerce."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template.write({"default_code": "WC-HTML", "taxes_id": [(5, 0, 0)]})
        cls.variant = cls.template.product_variant_id
        cls._bind_variant(cls.variant, 2001)

    def _template_values(self):
        return self._mapped_values("woocommerce.product.template", self.template)

    def _template_payload(self):
        return self._export_payload(
            "woocommerce.product.template", self.template, [1001]
        )

    def _variant_values(self):
        return self._mapped_values("woocommerce.product.product", self.variant)

    def _variant_payload(self):
        return self._export_payload(
            "woocommerce.product.product", self.variant, [1001, 2001]
        )

    def test_template_placeholder_is_no_value(self):
        self.template.public_description = PLACEHOLDER
        self.assertIsNone(self._template_values()["description"])

    def test_template_placeholder_clears_woocommerce(self):
        self.template.public_description = PLACEHOLDER
        self.assertEqual(self._template_payload()["description"], "")

    def test_template_text_is_kept(self):
        self.template.public_description = TEXT
        self.assertEqual(self._template_values()["description"], TEXT_HEX)
        self.assertEqual(self._template_payload()["description"], TEXT_HEX)

    def test_template_image_only_is_kept(self):
        self.template.public_description = IMAGE
        self.assertEqual(self._template_values()["description"], IMAGE)

    def test_single_variant_description_is_the_fallback(self):
        self.template.public_description = PLACEHOLDER
        self.variant.variant_public_description = TEXT
        self.assertEqual(self._template_values()["description"], TEXT_HEX)

    def test_single_variant_placeholder_is_no_value(self):
        self.template.public_description = PLACEHOLDER
        self.variant.variant_public_description = PLACEHOLDER
        self.assertIsNone(self._template_values()["description"])

    def test_variable_product_has_no_variant_fallback(self):
        template = self._create_variable_template()
        template.public_description = PLACEHOLDER
        template.product_variant_ids[0].variant_public_description = TEXT
        values = self._mapped_values("woocommerce.product.template", template)
        self.assertIsNone(values["description"])

    def test_short_description_no_value_clears_woocommerce(self):
        self.template.public_short_description = False
        self.assertIsNone(self._template_values()["short_description"])
        self.assertEqual(self._template_payload()["short_description"], "")

    def test_short_description_is_kept(self):
        self.template.public_short_description = "Short"
        self.assertEqual(self._template_values()["short_description"], "Short")

    def test_variant_placeholder_clears_woocommerce(self):
        self.variant.variant_public_description = PLACEHOLDER
        self.assertIsNone(self._variant_values()["description"])
        self.assertEqual(self._variant_payload()["description"], "")

    def test_variant_text_is_kept(self):
        self.variant.variant_public_description = TEXT
        self.assertEqual(self._variant_values()["description"], TEXT_HEX)
        self.assertEqual(self._variant_payload()["description"], TEXT_HEX)
