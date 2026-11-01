# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.osv import expression

from odoo.addons.l10n_es_aeat_mod303.tests.test_l10n_es_aeat_mod303 import (
    TestL10nEsAeatMod303Base,
)


class TestL10nEsAeatTaxLine(TestL10nEsAeatMod303Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model303.button_calculate()
        cls.model303_4t.button_calculate()
        map_line = cls.model303.tax_line_ids[0].map_line_id
        # A tax line of another report whose res_id is the id of a 303. Only the
        # model name matters: the 390 module need not be installed
        cls.mod390_tax_line = cls.env["l10n.es.aeat.tax.line"].create(
            {
                "model": "l10n.es.aeat.mod390.report",
                "res_id": cls.model303.id,
                "map_line_id": map_line.id,
            }
        )
        # A 303 tax line whose res_id points to no report
        cls.orphan_tax_line = cls.env["l10n.es.aeat.tax.line"].create(
            {
                "model": "l10n.es.aeat.mod303.report",
                "res_id": 0,
                "map_line_id": map_line.id,
            }
        )
        cls.tax_lines = cls.model303.tax_line_ids
        cls.tax_lines += cls.model303_4t.tax_line_ids
        cls.tax_lines += cls.mod390_tax_line
        cls.tax_lines += cls.orphan_tax_line

    def test_tax_line_search_mod303_in(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "in", self.model303.ids)]
        )
        self.assertEqual(tax_lines, self.model303.tax_line_ids)

    def test_tax_line_search_mod303_in_both(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [
                ("id", "in", self.tax_lines.ids),
                ("mod303_id", "in", [self.model303.id, self.model303_4t.id]),
            ]
        )
        self.assertEqual(
            tax_lines,
            self.model303.tax_line_ids + self.model303_4t.tax_line_ids,
        )

    def test_tax_line_search_mod303_equal(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "=", self.model303_4t.id)]
        )
        self.assertEqual(tax_lines, self.model303_4t.tax_line_ids)

    def test_tax_line_search_mod303_not_equal(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "!=", self.model303.id)]
        )
        self.assertEqual(
            tax_lines,
            self.model303_4t.tax_line_ids + self.mod390_tax_line + self.orphan_tax_line,
        )

    def test_tax_line_search_mod303_not_in(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [
                ("id", "in", self.tax_lines.ids),
                ("mod303_id", "not in", self.model303.ids),
            ]
        )
        self.assertEqual(
            tax_lines,
            self.model303_4t.tax_line_ids + self.mod390_tax_line + self.orphan_tax_line,
        )

    def test_tax_line_search_mod303_not_in_both(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [
                ("id", "in", self.tax_lines.ids),
                ("mod303_id", "not in", [self.model303.id, self.model303_4t.id]),
            ]
        )
        self.assertEqual(tax_lines, self.mod390_tax_line + self.orphan_tax_line)

    def test_tax_line_search_mod303_not_in_empty(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "not in", [])]
        )
        self.assertEqual(tax_lines, self.tax_lines)

    def test_tax_line_search_mod303_false(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "=", False)]
        )
        self.assertEqual(tax_lines, self.mod390_tax_line + self.orphan_tax_line)

    def test_tax_line_search_mod303_none(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "=", None)]
        )
        self.assertEqual(tax_lines, self.mod390_tax_line + self.orphan_tax_line)

    def test_tax_line_search_mod303_not_false(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_id", "!=", False)]
        )
        self.assertEqual(
            tax_lines,
            self.model303.tax_line_ids + self.model303_4t.tax_line_ids,
        )

    def test_tax_line_search_mod303_in_or_false(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [
                ("id", "in", self.tax_lines.ids),
                ("mod303_id", "in", [self.model303.id, False]),
            ]
        )
        self.assertEqual(
            tax_lines,
            self.model303.tax_line_ids + self.mod390_tax_line + self.orphan_tax_line,
        )

    def test_tax_line_search_mod303_not_in_nor_false(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [
                ("id", "in", self.tax_lines.ids),
                ("mod303_id", "not in", [self.model303.id, False]),
            ]
        )
        self.assertEqual(tax_lines, self.model303_4t.tax_line_ids)

    def test_tax_line_search_mod303_period_type(self):
        tax_lines = self.env["l10n.es.aeat.tax.line"].search(
            [("id", "in", self.tax_lines.ids), ("mod303_period_type", "=", "4T")]
        )
        self.assertEqual(tax_lines, self.model303_4t.tax_line_ids)

    def test_tax_line_search_mod303_unsupported_operator(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search(
                [("mod303_id", "ilike", self.model303.ids)]
            )

    def test_tax_line_search_mod303_name(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search(
                [("mod303_id", "=", self.model303.name)]
            )

    def test_tax_line_search_mod303_true(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search([("mod303_id", "=", True)])

    def test_tax_line_search_mod303_record(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search(
                [("mod303_id", "=", self.model303)]
            )

    def test_tax_line_search_mod303_zero(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search([("mod303_id", "in", [0])])

    def test_tax_line_search_mod303_none_in_list(self):
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search(
                [("mod303_id", "in", [self.model303.id, None])]
            )

    def test_tax_line_search_mod303_not_in_subquery(self):
        reports_4t = self.env["l10n.es.aeat.mod303.report"]._search(
            [("period_type", "=", "4T")]
        )
        with self.assertRaises(NotImplementedError):
            self.env["l10n.es.aeat.tax.line"].search(
                [("mod303_id", "not in", reports_4t)]
            )

    def test_tax_line_write_res_id(self):
        tax_line = self.model303.tax_line_ids[0]
        self.assertEqual(tax_line.mod303_id, self.model303)
        tax_line.write({"res_id": self.model303_4t.id})
        self.assertEqual(tax_line.mod303_id, self.model303_4t)

    def test_tax_line_write_model(self):
        tax_line = self.model303.tax_line_ids[0]
        self.assertEqual(tax_line.mod303_id, self.model303)
        tax_line.write({"model": "l10n.es.aeat.mod390.report"})
        self.assertFalse(tax_line.mod303_id)

    def test_mod303_write_period_type_refreshes_lines_without_error(self):
        tax_line = self.model303_4t.tax_line_ids[0]
        self.assertEqual(tax_line.mod303_period_type, "4T")
        with patch.object(expression._logger, "error") as logger_error:
            self.model303_4t.write({"period_type": "3T"})
        logger_error.assert_not_called()
        self.assertEqual(tax_line.mod303_period_type, "3T")
