# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUnlinkListeners(TransactionCase):
    """Deleting partners and product templates must work and enqueue the
    deprecation of the affected Oxigesti pricelist item bindings.

    Regression for the production crash where both ``on_record_unlink``
    listeners called ``get_external_ids_domain_by_backend()``, a method
    that does not exist anywhere in the module: every partner has a
    pricelist, so deleting ANY partner (or product template) raised an
    ``AttributeError`` and the deletion was rolled back, even when there
    was no Oxigesti binding involved at all.
    """

    def setUp(self):
        super().setUp()
        self.backend = self.env["oxigesti.backend"].create(
            {
                "name": "Test unreachable",
                "server": "127.0.0.1",
                "port": 1,
                "database": "irrelevant",
                "schema": "dbo",
                "username": "irrelevant",
                "password": "irrelevant",
                "lang_id": self.env.ref("base.lang_en").id,
                "tz": "UTC",
                "chunk_size": 0,
            }
        )
        self.template = self.env["product.template"].create(
            {"name": "Oxigesti unlink test product", "default_code": "OXTEST01"}
        )
        self.pricelist = self.env["product.pricelist"].create(
            {"name": "Oxigesti unlink test pricelist"}
        )
        self.item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "compute_price": "fixed",
                "fixed_price": 10.0,
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Oxigesti unlink test partner"}
        )
        self.partner.property_product_pricelist = self.pricelist

    def _make_binding(self):
        return self.env["oxigesti.product.pricelist.item"].create(
            {
                "backend_id": self.backend.id,
                "odoo_id": self.item.id,
                "odoo_partner_id": self.partner.id,
                "external_id": json.dumps(["OXTEST01", "MUT01"]),
            }
        )

    def _deprecation_jobs(self):
        return self.env["queue.job"].search(
            [
                ("model_name", "=", "oxigesti.product.pricelist.item"),
                ("method_name", "=", "export_delete_record"),
            ]
        )

    def test_unlink_partner_without_bindings(self):
        """The exact production symptom: a plain partner with no Oxigesti
        binding could not be deleted because the listener always runs."""
        self.partner.unlink()
        self.assertFalse(self.partner.exists())
        self.assertFalse(self._deprecation_jobs())

    def test_unlink_partner_with_binding_enqueues_deprecation(self):
        """Deleting a partner with an exported price must enqueue one
        deprecation job per external id, then delete normally."""
        self._make_binding()
        self.partner.unlink()
        self.assertFalse(self.partner.exists())
        jobs = self._deprecation_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertIn("OXTEST01", str(jobs.args))

    def test_unlink_template_without_bindings(self):
        """A product template with no bound pricelist item must be
        deletable (same nonexistent-method crash as the partner case)."""
        self.template.unlink()
        self.assertFalse(self.template.exists())
        self.assertFalse(self._deprecation_jobs())

    def test_unlink_template_with_binding_enqueues_deprecation(self):
        """Deleting a product template must enqueue the deprecation of the
        pricelist item bindings referencing it: the items are removed by a
        database-level cascade, so their own unlink listener never runs."""
        self._make_binding()
        self.template.unlink()
        self.assertFalse(self.template.exists())
        jobs = self._deprecation_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertIn("OXTEST01", str(jobs.args))
