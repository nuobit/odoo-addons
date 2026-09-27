# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import (
    PLACEHOLDER,
    TEXT,
    BlankHtmlMigrationMixin,
)

from .common import WooCommerceWPMLCase


class TestReexportBlankHtmlWPML(BlankHtmlMigrationMixin, WooCommerceWPMLCase):
    def test_placeholder_in_secondary_export_language(self):
        english = self.template.with_context(lang="en_US")
        spanish = self.template.with_context(lang="es_ES")
        english.public_description = TEXT
        spanish.public_description = PLACEHOLDER
        self._start_incremental_exports()
        self._run_migration("connector_woocommerce", "14.0.0.2.1", "14.0.0.2.0")
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assertEqual(english.public_description, TEXT)
        self.assertEqual(spanish.public_description, PLACEHOLDER)

    def test_language_not_exported_is_not_selected(self):
        self.template.with_context(lang="en_US").public_description = TEXT
        self.template.with_context(lang="es_ES").public_description = PLACEHOLDER
        self.backend.lang_ids = self.env.ref("base.lang_en")
        self._start_incremental_exports()
        self._run_migration("connector_woocommerce", "14.0.0.2.1", "14.0.0.2.0")
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.env["product.template"],
        )
