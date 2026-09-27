# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import PLACEHOLDER, TEXT, TEXT_HEX

from .common import WooCommerceWPMLCase


class TestExportMapperHtmlWPML(WooCommerceWPMLCase):
    """Each export language is judged on its own text."""

    def test_template_description_per_language(self):
        english = self.template.with_context(lang="en_US")
        spanish = self.template.with_context(lang="es_ES")
        english.public_description = TEXT
        spanish.public_description = PLACEHOLDER
        with self.backend.work_on("woocommerce.product.template") as work:
            mapper = work.component(usage="export.mapper")
            self.assertEqual(mapper._get_product_description(english), TEXT_HEX)
            self.assertIsNone(mapper._get_product_description(spanish))

    def test_variant_description_per_language(self):
        variant = self.template.product_variant_id
        variant.with_context(lang="en_US").variant_public_description = PLACEHOLDER
        variant.with_context(lang="es_ES").variant_public_description = TEXT
        english = self.template.with_context(lang="en_US")
        spanish = self.template.with_context(lang="es_ES")
        with self.backend.work_on("woocommerce.product.template") as work:
            mapper = work.component(usage="export.mapper")
            self.assertIsNone(mapper._get_product_variant_description(english))
            self.assertEqual(mapper._get_product_variant_description(spanish), TEXT_HEX)
        with self.backend.work_on("woocommerce.product.product") as work:
            mapper = work.component(usage="export.mapper")
            self.assertIsNone(
                mapper._get_product_description(variant.with_context(lang="en_US"))
            )
            self.assertEqual(
                mapper._get_product_description(variant.with_context(lang="es_ES")),
                TEXT_HEX,
            )
