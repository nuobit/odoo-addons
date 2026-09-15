# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command

from odoo.addons.l10n_es_aeat_sii_oca.tests.test_l10n_es_aeat_sii import (
    TestL10nEsAeatSiiBase,
)


class TestL10nEsAeatSiiOcaExtension(TestL10nEsAeatSiiBase):
    def _create_invoice_with_taxes(self, move_type, lines, extra_vals=None):
        """Draft invoice with a line per (price_unit, tax template xml-id suffixes)."""
        key_type = "sale" if move_type.startswith("out_") else "purchase"
        vals = {
            "name": "TEST001",
            "partner_id": self.partner.id,
            "invoice_date": "2020-01-01",
            "move_type": move_type,
            "sii_registration_key": self.env["aeat.sii.mapping.registration.keys"]
            .search([("code", "=", "01"), ("type", "=", key_type)], limit=1)
            .id,
            "invoice_line_ids": [],
        }
        for price_unit, tax_codes in lines:
            taxes = self.company._get_taxes_from_xmlids(
                [f"account_tax_template_{code}" for code in tax_codes]
            )
            vals["invoice_line_ids"].append(
                Command.create(
                    {
                        "product_id": self.product.id,
                        "account_id": self.account_expense.id,
                        "name": "Test line",
                        "price_unit": price_unit,
                        "quantity": 1,
                        "tax_ids": [Command.set(taxes.ids)],
                    }
                )
            )
        vals.update(extra_vals or {})
        return self.env["account.move"].create(vals)

    def test_out_invoice_sdd_exempt_tax(self):
        """The SDD exempt tax is mapped as an exempt service (SFESSE)."""
        sdd_tax = self.company._get_taxes_from_xmlids(
            ["account_tax_template_s_iva0_sdd"]
        )
        sfesse_line = self.env.ref("l10n_es_aeat_sii_oca.aeat_sii_map_line_SFESSE")
        self.assertIn(
            sdd_tax,
            self.company._get_taxes_from_xmlids(
                sfesse_line.tax_xmlid_ids.mapped("name")
            ),
        )
        self.product.sii_exempt_cause = "E1"
        invoice = self._create_invoice_with_taxes(
            "out_invoice", [(100, ["s_iva0_sdd"])]
        )
        res = invoice._get_aeat_invoice_dict()["FacturaExpedida"]
        self.assertEqual(
            res["TipoDesglose"],
            {
                "DesgloseFactura": {
                    "Sujeta": {
                        "Exenta": {
                            "DetalleExenta": [
                                {"CausaExencion": "E1", "BaseImponible": 100.0}
                            ]
                        }
                    }
                }
            },
        )

    def test_in_invoice_partially_deductible_tax(self):
        """CuotaDeducible only takes the tax repartition lines with an account."""
        tax = self.env["account.tax"].browse(
            self.company._get_tax_id_from_xmlid("account_tax_template_p_iva21_bc")
        )
        # 50 % of the tax goes to the VAT account (deductible), 50 % to the expense
        tax.write(
            {
                "repartition_line_ids": [
                    Command.update(line.id, {"factor_percent": 50})
                    for line in tax.repartition_line_ids.filtered(
                        lambda x: x.repartition_type == "tax"
                    )
                ]
                + [
                    Command.create(
                        {
                            "repartition_type": "tax",
                            "document_type": document_type,
                            "factor_percent": 50,
                        }
                    )
                    for document_type in ("invoice", "refund")
                ]
            }
        )
        invoice = self._create_invoice_with_taxes(
            "in_invoice", [(100, ["p_iva21_bc"])], {"ref": "SUP001"}
        )
        res = invoice._get_aeat_invoice_dict()["FacturaRecibida"]
        self.assertEqual(
            res["DesgloseFactura"]["DesgloseIVA"]["DetalleIVA"],
            [
                {
                    "TipoImpositivo": "21.0",
                    "BaseImponible": 100.0,
                    "CuotaSoportada": 21.0,
                }
            ],
        )
        self.assertEqual(res["CuotaDeducible"], 10.5)

    def test_out_invoice_registration_key_06(self):
        """Key 06 merges the operation type breakdown and adds BaseImponibleACoste."""
        # The intra-community fiscal position forces the DesgloseTipoOperacion
        # breakdown, that splits goods (Entrega) and services (PrestacionServicios)
        invoice = self._create_invoice_with_taxes(
            "out_invoice",
            [(100, ["s_iva21b"]), (100, ["s_iva21s"])],
            {
                "fiscal_position_id": self.fp_intra.id,
                "sii_registration_key": self.env.ref(
                    "l10n_es_aeat_sii_oca.aeat_sii_mapping_registration_keys_06"
                ).id,
            },
        )
        res = invoice._get_aeat_invoice_dict()["FacturaExpedida"]
        self.assertEqual(
            res["TipoDesglose"],
            {
                "DesgloseFactura": {
                    "Sujeta": {
                        "NoExenta": {
                            "TipoNoExenta": "S1",
                            "DesgloseIVA": {
                                "DetalleIVA": [
                                    {
                                        "TipoImpositivo": "21.0",
                                        "BaseImponible": 200.0,
                                        "CuotaRepercutida": 42.0,
                                    }
                                ]
                            },
                        }
                    }
                }
            },
        )
        self.assertEqual(res["BaseImponibleACoste"], 200.0)

    def test_in_invoice_registration_key_06(self):
        """Key 06 adds BaseImponibleACoste to received invoices."""
        invoice = self._create_invoice_with_taxes(
            "in_invoice",
            [(100, ["p_iva21_bc"]), (100, ["p_iva21_sc"])],
            {
                "ref": "SUP001",
                "sii_registration_key": self.env.ref(
                    "l10n_es_aeat_sii_oca.aeat_sii_mapping_registration_keys_21"
                ).id,
            },
        )
        res = invoice._get_aeat_invoice_dict()["FacturaRecibida"]
        self.assertEqual(res["ClaveRegimenEspecialOTrascendencia"], "06")
        self.assertEqual(res["BaseImponibleACoste"], 200.0)
        self.assertEqual(res["CuotaDeducible"], 42.0)
