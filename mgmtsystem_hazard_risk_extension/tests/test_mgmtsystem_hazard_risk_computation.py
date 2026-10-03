# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase, TransactionCase, tagged

from ..hooks import post_init_hook, uninstall_hook


@tagged("post_install", "-at_install")
class TestLanguageInstall(TransactionCase):
    def test_language_install_translates_formula(self):
        formula = self.env.ref("mgmtsystem_hazard_risk.risk_computation_a_times_b")
        # Start without translations, whatever languages the database has active
        self.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                ("res_id", "=", formula.id),
            ]
        ).unlink()
        self.env["base.language.install"].create({"lang": "es_ES"}).lang_install()
        self.env["base.language.install"].create({"lang": "ca_ES"}).lang_install()
        self.assertEqual(
            formula.with_context(lang="es_ES").description,
            "Riesgo = Probabilidad (A) x Severidad (B)",
        )
        self.assertEqual(
            formula.with_context(lang="ca_ES").description,
            "Risc = Probabilitat (A) x Severitat (B)",
        )


@tagged("post_install", "-at_install")
class TestTranslationHooks(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # es_MX is covered by the module's es.po; pt_PT by none of its files
        for lang in ("es_ES", "ca_ES", "es_MX", "pt_PT"):
            cls.env["res.lang"]._activate_lang(lang)
        cls.formula = cls.env.ref("mgmtsystem_hazard_risk.risk_computation_a_times_b")
        # Start without translations, whatever the database holds
        cls.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                ("res_id", "=", cls.formula.id),
            ]
        ).unlink()
        owner = cls.env.ref("base.module_mgmtsystem_hazard_risk")
        owner._update_translations(["es_ES"])
        module = cls.env.ref("base.module_mgmtsystem_hazard_risk_extension")
        module._update_translations(["es_ES", "ca_ES", "es_MX"])

    def test_install_replaces_stored_translations(self):
        self.formula.with_context(lang="es_ES").description = "Stored wording"
        self.formula.with_context(lang="es_MX").description = "Stored wording"
        post_init_hook(self.env.cr, self.registry)
        self.assertEqual(
            self.formula.with_context(lang="es_ES").description,
            "Riesgo = Probabilidad (A) x Severidad (B)",
        )
        self.assertEqual(
            self.formula.with_context(lang="es_MX").description,
            "Riesgo = Probabilidad (A) x Severidad (B)",
        )

    def test_reload_refreshes_description_read_before(self):
        self.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                ("res_id", "=", self.formula.id),
            ]
        ).unlink()
        # Reading it caches the English source: the reload must refresh it
        self.assertEqual(
            self.formula.with_context(lang="es_ES").description,
            "Risk = Probability (A) x Severity (B)",
        )
        self.formula._reload_description_translations(
            "mgmtsystem_hazard_risk_extension"
        )
        self.assertEqual(
            self.formula.with_context(lang="es_ES").description,
            "Riesgo = Probabilidad (A) x Severidad (B)",
        )

    def test_reload_refreshes_other_formula_read_before(self):
        other_formula = self.env.ref("mgmtsystem_hazard_risk.risk_computation_a_plus_b")
        # The reload then finds nothing to delete, so only its invalidation can
        # refresh the other formula: a delete clears the whole cache
        self.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                ("res_id", "in", [self.formula.id, other_formula.id]),
            ]
        ).unlink()
        # Reading it caches the English source: the reload must refresh it
        self.assertEqual(
            other_formula.with_context(lang="es_ES").description,
            "Risk = Probability (A) + Severity (B)",
        )
        self.formula._reload_description_translations(
            "mgmtsystem_hazard_risk_extension"
        )
        self.assertEqual(
            other_formula.with_context(lang="es_ES").description,
            "Riesgo = Probabilidad (A) + Severidad (B)",
        )

    def test_uninstall_removes_translations(self):
        domain = [
            ("type", "=", "model"),
            ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
            ("res_id", "=", self.formula.id),
        ]
        self.assertEqual(
            self.env["ir.translation"].search(domain, order="lang").mapped("lang"),
            ["ca_ES", "es_ES", "es_MX"],
        )
        uninstall_hook(self.env.cr, self.registry)
        self.assertFalse(self.env["ir.translation"].search(domain))

    def test_uninstall_keeps_owner_translation_edited_by_hand(self):
        label_field = self.env.ref(
            "mgmtsystem_hazard_risk.field_mgmtsystem_hazard_risk_computation__name"
        )
        label = self.env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", "ir.model.fields,field_description"),
                ("res_id", "=", label_field.id),
                ("lang", "=", "es_ES"),
            ]
        )
        self.assertEqual(len(label), 1)
        label.value = "Edited by hand"
        uninstall_hook(self.env.cr, self.registry)
        # The translations change behind the ORM cache: read them from the database
        label.invalidate_cache()
        self.assertEqual(label.value, "Edited by hand")

    def test_uninstall_keeps_translation_of_language_not_shipped(self):
        self.formula.with_context(lang="pt_PT").description = "Written by hand"
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(
            self.formula.with_context(lang="pt_PT").description, "Written by hand"
        )
