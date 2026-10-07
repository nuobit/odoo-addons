# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from psycopg2 import sql

from .common import WooCommerceCase


class TestTranslationExportSince(WooCommerceCase):
    """A translation saved on its own, as the translation dialog does, gets
    the attribute value, attribute or category it translates into the next
    export by date."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("es_ES")
        cls.attribute = cls.env["product.attribute"].create({"name": "Size"})
        cls.value = cls.env["product.attribute.value"].create(
            {"name": "One size", "attribute_id": cls.attribute.id}
        )
        cls.public_category = cls.env["product.public.category"].create(
            {"name": "Masks", "slug_name": "masks"}
        )

    def _set_write_date(self, record, write_date):
        # The database stamps write dates with the time the transaction
        # started, the same for the whole test: an older one is set by hand.
        self.env["base"].flush()
        self.env.cr.execute(
            sql.SQL("UPDATE {} SET write_date = %s WHERE id = %s").format(
                sql.Identifier(record._table)
            ),
            (write_date, record.id),
        )
        record.invalidate_cache(["write_date"], record.ids)

    def _selection_of(self, binding_model, action, record):
        job = self._new_job(binding_model, "export_batch", action)
        return (
            self.env[record._name]
            .with_context(active_test=False)
            .search([("id", "=", record.id)] + job.kwargs["domain"])
        )

    def test_new_translation_selects_attribute_value(self):
        self._set_write_date(self.value, "2000-01-01 00:00:00")
        self.backend.export_product_attribute_value_since_date = "2000-01-02 00:00:00"
        self._translate(self.value, "name", "Talla única")
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.attribute.value",
                self.backend.export_product_attribute_value_since,
                self.value,
            ),
            self.value,
        )

    def test_changed_translation_selects_attribute_value(self):
        self._translate(self.value, "name", "Talla única")
        self._set_write_date(self.value, "2000-01-01 00:00:00")
        self.backend.export_product_attribute_value_since_date = "2000-01-02 00:00:00"
        self._translate(self.value, "name", "Única")
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.attribute.value",
                self.backend.export_product_attribute_value_since,
                self.value,
            ),
            self.value,
        )

    def test_removed_translation_selects_attribute_value(self):
        translation = self._translate(self.value, "name", "Talla única")
        self._set_write_date(self.value, "2000-01-01 00:00:00")
        self.backend.export_product_attribute_value_since_date = "2000-01-02 00:00:00"
        translation.unlink()
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.attribute.value",
                self.backend.export_product_attribute_value_since,
                self.value,
            ),
            self.value,
        )

    def test_untranslated_attribute_value_is_not_selected(self):
        other_value = self.env["product.attribute.value"].create(
            {"name": "Large", "attribute_id": self.attribute.id}
        )
        self._set_write_date(self.value, "2000-01-01 00:00:00")
        self.backend.export_product_attribute_value_since_date = "2000-01-02 00:00:00"
        self._translate(other_value, "name", "Grande")
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.attribute.value",
                self.backend.export_product_attribute_value_since,
                self.value,
            ),
            self.env["product.attribute.value"],
        )

    def test_new_translation_selects_attribute(self):
        self._set_write_date(self.attribute, "2000-01-01 00:00:00")
        self.backend.export_product_attribute_since_date = "2000-01-02 00:00:00"
        self._translate(self.attribute, "name", "Talla")
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.attribute",
                self.backend.export_product_attribute_since,
                self.attribute,
            ),
            self.attribute,
        )

    def test_new_translation_selects_category(self):
        self._set_write_date(self.public_category, "2000-01-01 00:00:00")
        self.backend.export_product_public_category_since_date = "2000-01-02 00:00:00"
        self._translate(self.public_category, "name", "Mascarillas")
        self.assertEqual(
            self._selection_of(
                "woocommerce.product.public.category",
                self.backend.export_product_public_category_since,
                self.public_category,
            ),
            self.public_category,
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

    def test_translation_of_other_model_keeps_its_write_date(self):
        title = self.env["res.partner.title"].create({"name": "Madam"})
        self._set_write_date(title, "2000-01-01 00:00:00")
        self._translate(title, "name", "Señora")
        self.assertEqual(title.write_date, datetime(2000, 1, 1))
