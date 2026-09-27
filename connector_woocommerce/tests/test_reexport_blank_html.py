# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import PLACEHOLDER, TEXT, BlankHtmlMigrationMixin, WooCommerceCase


class TestReexportBlankHtml(BlankHtmlMigrationMixin, WooCommerceCase):
    def _migrate(self):
        self._run_migration("connector_woocommerce", "14.0.0.2.1", "14.0.0.2.0")

    def test_only_bound_placeholder_is_selected(self):
        self.template.public_description = PLACEHOLDER
        self.unbound_template.public_description = PLACEHOLDER
        content = self._create_template("Real description", 1002)
        content.public_description = TEXT
        image = self._create_template("Image description", 1004)
        image.public_description = '<p><img src="/image.png"/></p>'
        empty = self._create_template("Already empty description", 1005)
        self._start_incremental_exports()
        self._migrate()
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assertEqual(self.template.public_description, PLACEHOLDER)
        self.assertEqual(self.unbound_template.public_description, PLACEHOLDER)
        self.assertEqual(content.public_description, TEXT)
        self.assertEqual(image.public_description, '<p><img src="/image.png"/></p>')
        self.assertFalse(empty.public_description)

    def test_single_variant_fallback_is_selected(self):
        self.template.product_variant_id.variant_public_description = PLACEHOLDER
        content = self._create_template("Template description takes precedence", 1002)
        content.public_description = TEXT
        content.product_variant_id.variant_public_description = PLACEHOLDER
        self._start_incremental_exports()
        self._migrate()
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assertEqual(
            self.template.product_variant_id.variant_public_description, PLACEHOLDER
        )

    def test_variable_template_reaches_the_variant_batch(self):
        template = self._create_variable_template()
        template.public_description = PLACEHOLDER
        self._start_incremental_exports()
        self._migrate()
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.env["product.template"],
        )
        self._assert_export_selection(
            "woocommerce.product.product",
            self.backend.export_products_since,
            template.product_variant_ids,
        )

    def test_bound_variant_does_not_mark_its_clean_sibling(self):
        template = self._create_variable_template()
        first, second = template.product_variant_ids.sorted("id")
        self._bind_variant(first, 2001)
        self._bind_variant(second, 2002)
        first.variant_public_description = PLACEHOLDER
        second.variant_public_description = TEXT
        self._start_incremental_exports()
        self._migrate()
        self._assert_export_selection(
            "woocommerce.product.product", self.backend.export_products_since, first
        )
        self.assertEqual(first.variant_public_description, PLACEHOLDER)
        self.assertEqual(second.variant_public_description, TEXT)

    def test_archived_bound_template_is_still_selected(self):
        self.template.public_description = PLACEHOLDER
        self.template.action_archive()
        self._start_incremental_exports()
        self._migrate()
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assertFalse(self.template.active)
