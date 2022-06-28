# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.l10n_es_aeat_sii_oca.models.account_move import round_by_keys


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_tax_info(self):
        self.ensure_one()
        res = {}
        for line in self.line_ids:
            sign = -1 if self.move_type[:3] == "out" else 1
            for tax in line.tax_ids:
                taxes = tax.amount_type == "group" and tax.children_tax_ids or tax
                for tax in taxes:
                    res.setdefault(
                        tax,
                        {"tax": tax, "base": 0, "amount": 0, "deductible_amount": 0},
                    )
                    res[tax]["base"] += line.balance * sign
            if line.tax_line_id:
                tax = line.tax_line_id
                if "invoice" in self.move_type:
                    repartition_lines = tax.invoice_repartition_line_ids
                else:
                    repartition_lines = tax.refund_repartition_line_ids
                if (
                    len(repartition_lines) > 2
                    and line.tax_repartition_line_id.factor_percent < 0
                ):
                    # taxes with more than one "tax" repartition line must be discarded
                    continue
                res.setdefault(
                    tax, {"tax": tax, "base": 0, "amount": 0, "deductible_amount": 0}
                )
                res[tax]["amount"] += line.balance * sign
                if line.tax_repartition_line_id.account_id:
                    res[tax]["deductible_amount"] += line.balance * sign
        return res

    def _get_sii_out_taxes(self, tax_lines):  # noqa: C901
        """Get the taxes for sales invoices.

        :param self: Single invoice record.
        """
        self.ensure_one()
        taxes_dict = {}
        taxes_sfesb = self._get_sii_taxes_map(["SFESB"])
        taxes_sfesbe = self._get_sii_taxes_map(["SFESBE"])
        taxes_sfesisp = self._get_sii_taxes_map(["SFESISP"])
        # taxes_sfesisps = self._get_taxes_map(['SFESISPS'])
        taxes_sfens = self._get_sii_taxes_map(["SFENS"])
        taxes_sfess = self._get_sii_taxes_map(["SFESS"])
        taxes_sfesse = self._get_sii_taxes_map(["SFESSE"])
        taxes_sfesns = self._get_sii_taxes_map(["SFESNS"])
        taxes_not_in_total = self._get_sii_taxes_map(["NotIncludedInTotal"])
        taxes_not_in_total_neg = self._get_sii_taxes_map(["NotIncludedInTotalNegative"])
        base_not_in_total = self._get_sii_taxes_map(["BaseNotIncludedInTotal"])
        not_in_amount_total = 0
        exempt_cause = self._get_sii_exempt_cause(taxes_sfesbe + taxes_sfesse)
        for tax_line in tax_lines.values():
            tax = tax_line["tax"]
            breakdown_taxes = taxes_sfesb + taxes_sfesisp + taxes_sfens + taxes_sfesbe
            if tax in taxes_not_in_total:
                not_in_amount_total += tax_line["amount"]
            elif tax in taxes_not_in_total_neg:
                not_in_amount_total -= tax_line["amount"]
            elif tax in base_not_in_total:
                not_in_amount_total += tax_line["base"]
            if tax in breakdown_taxes:
                tax_breakdown = taxes_dict.setdefault("DesgloseFactura", {})
            if tax in (taxes_sfesb + taxes_sfesbe + taxes_sfesisp):
                sub_dict = tax_breakdown.setdefault("Sujeta", {})
                # TODO l10n_es no tiene impuesto exento de bienes
                # corrientes nacionales
                if tax in taxes_sfesbe:
                    exempt_dict = sub_dict.setdefault(
                        "Exenta",
                        {"DetalleExenta": [{"BaseImponible": 0}]},
                    )
                    det_dict = exempt_dict["DetalleExenta"][0]
                    if exempt_cause:
                        det_dict["CausaExencion"] = exempt_cause
                    det_dict["BaseImponible"] += tax_line["base"]
                else:
                    sub_dict.setdefault(
                        "NoExenta",
                        {
                            "TipoNoExenta": ("S2" if tax in taxes_sfesisp else "S1"),
                            "DesgloseIVA": {"DetalleIVA": []},
                        },
                    )
                    not_ex_type = sub_dict["NoExenta"]["TipoNoExenta"]
                    if tax in taxes_sfesisp:
                        is_s3 = not_ex_type == "S1"
                    else:
                        is_s3 = not_ex_type == "S2"
                    if is_s3:
                        sub_dict["NoExenta"]["TipoNoExenta"] = "S3"
                    sub_dict["NoExenta"]["DesgloseIVA"]["DetalleIVA"].append(
                        self._get_sii_tax_dict(tax_line, tax_lines),
                    )
            # No sujetas
            if tax in taxes_sfens:
                # ImporteTAIReglasLocalizacion or ImportePorArticulos7_14_Otros
                default_no_taxable_cause = self._get_no_taxable_cause()
                nsub_dict = tax_breakdown.setdefault(
                    "NoSujeta",
                    {default_no_taxable_cause: 0},
                )
                nsub_dict[default_no_taxable_cause] += tax_line["base"]
            if tax in (taxes_sfess + taxes_sfesse + taxes_sfesns):
                type_breakdown = taxes_dict.setdefault(
                    "DesgloseTipoOperacion",
                    {"PrestacionServicios": {}},
                )
                if tax in (taxes_sfesse + taxes_sfess):
                    type_breakdown["PrestacionServicios"].setdefault("Sujeta", {})
                service_dict = type_breakdown["PrestacionServicios"]
                if tax in taxes_sfesse:
                    exempt_dict = service_dict["Sujeta"].setdefault(
                        "Exenta",
                        {"DetalleExenta": [{"BaseImponible": 0}]},
                    )
                    det_dict = exempt_dict["DetalleExenta"][0]
                    if exempt_cause:
                        det_dict["CausaExencion"] = exempt_cause
                    det_dict["BaseImponible"] += tax_line["base"]
                if tax in taxes_sfess:
                    # TODO l10n_es_ no tiene impuesto ISP de servicios
                    # if tax in taxes_sfesisps:
                    #     TipoNoExenta = 'S2'
                    # else:
                    service_dict["Sujeta"].setdefault(
                        "NoExenta",
                        {"TipoNoExenta": "S1", "DesgloseIVA": {"DetalleIVA": []}},
                    )
                    sub = type_breakdown["PrestacionServicios"]["Sujeta"]["NoExenta"][
                        "DesgloseIVA"
                    ]["DetalleIVA"]
                    sub.append(self._get_sii_tax_dict(tax_line, tax_lines))
                if tax in taxes_sfesns:
                    nsub_dict = service_dict.setdefault(
                        "NoSujeta",
                        {"ImporteTAIReglasLocalizacion": 0},
                    )
                    nsub_dict["ImporteTAIReglasLocalizacion"] += tax_line["base"]
        # Ajustes finales breakdown
        # - DesgloseFactura y DesgloseTipoOperacion son excluyentes
        # - Ciertos condicionantes obligan DesgloseTipoOperacion
        if self._is_sii_type_breakdown_required(taxes_dict):
            taxes_dict.setdefault("DesgloseTipoOperacion", {})
            taxes_dict["DesgloseTipoOperacion"]["Entrega"] = taxes_dict[
                "DesgloseFactura"
            ]
            del taxes_dict["DesgloseFactura"]
        return taxes_dict, not_in_amount_total

    def _get_sii_in_taxes(self, tax_lines):
        """Get the taxes for purchase invoices.

        :param self:  Single invoice record.
        """
        self.ensure_one()
        taxes_dict = {}
        taxes_sfrs = self._get_sii_taxes_map(["SFRS"])
        taxes_sfrsa = self._get_sii_taxes_map(["SFRSA"])
        taxes_sfrisp = self._get_sii_taxes_map(["SFRISP"])
        taxes_sfrns = self._get_sii_taxes_map(["SFRNS"])
        taxes_sfrnd = self._get_sii_taxes_map(["SFRND"])
        taxes_not_in_total = self._get_sii_taxes_map(["NotIncludedInTotal"])
        taxes_not_in_total_neg = self._get_sii_taxes_map(["NotIncludedInTotalNegative"])
        base_not_in_total = self._get_sii_taxes_map(["BaseNotIncludedInTotal"])
        tax_amount = 0.0
        tax_deductible_amount = 0.0
        not_in_amount_total = 0.0
        for tax_line in tax_lines.values():
            tax = tax_line["tax"]
            if tax in taxes_not_in_total:
                not_in_amount_total += tax_line["amount"]
            elif tax in taxes_not_in_total_neg:
                not_in_amount_total -= tax_line["amount"]
            elif tax in base_not_in_total:
                not_in_amount_total += tax_line["base"]
            if tax in taxes_sfrisp:
                base_dict = taxes_dict.setdefault(
                    "InversionSujetoPasivo",
                    {"DetalleIVA": []},
                )
            elif tax in taxes_sfrs + taxes_sfrns + taxes_sfrsa + taxes_sfrnd:
                base_dict = taxes_dict.setdefault("DesgloseIVA", {"DetalleIVA": []})
            else:
                continue
            tax_dict = self._get_sii_tax_dict(tax_line, tax_lines)
            if tax in taxes_sfrisp + taxes_sfrs:
                tax_amount += tax_line["amount"]
                tax_deductible_amount += tax_line["deductible_amount"]
            if tax in taxes_sfrns:
                tax_dict.pop("TipoImpositivo")
                tax_dict.pop("CuotaSoportada")
                base_dict["DetalleIVA"].append(tax_dict)
            elif tax in taxes_sfrsa:
                tax_dict["PorcentCompensacionREAGYP"] = tax_dict.pop("TipoImpositivo")
                tax_dict["ImporteCompensacionREAGYP"] = tax_dict.pop("CuotaSoportada")
                base_dict["DetalleIVA"].append(tax_dict)
            else:
                if not self._merge_tax_dict(
                    base_dict["DetalleIVA"],
                    tax_dict,
                    "TipoImpositivo",
                    ["BaseImponible", "CuotaSoportada"],
                ):
                    base_dict["DetalleIVA"].append(tax_dict)
        return taxes_dict, tax_amount, tax_deductible_amount, not_in_amount_total

    def _get_sii_base_cost(self, tax_lines):
        self.ensure_one()
        return sum([x["base"] for x in tax_lines.values()])

    def _get_sii_invoice_dict_out(self, cancel=False):
        """Build dict with data to send to AEAT WS for invoice types:
        out_invoice and out_refund.

        :param cancel: It indicates if the dictionary is for sending a
          cancellation of the invoice.
        :return: invoices (dict) : Dict XML with data for this invoice.
        """
        self.ensure_one()
        invoice_date = self._change_date_format(self.invoice_date)
        partner = self._sii_get_partner()
        company = self.company_id
        ejercicio = fields.Date.to_date(self.date).year
        periodo = "%02d" % fields.Date.to_date(self.date).month
        is_simplified_invoice = self._is_sii_simplified_invoice()
        serial_number = (self.name or "")[0:60]
        if self.thirdparty_invoice:
            serial_number = self.thirdparty_number[0:60]
        inv_dict = {
            "IDFactura": {
                "IDEmisorFactura": {"NIF": company.vat[2:]},
                # On cancelled invoices, number is not filled
                "NumSerieFacturaEmisor": serial_number,
                "FechaExpedicionFacturaEmisor": invoice_date,
            },
            "PeriodoLiquidacion": {"Ejercicio": ejercicio, "Periodo": periodo},
        }
        if not cancel:
            tax_lines = self._get_tax_info()
            tipo_desglose, not_in_amount_total = self._get_sii_out_taxes(tax_lines)
            amount_total = self.amount_total_signed - not_in_amount_total
            inv_dict["FacturaExpedida"] = {
                "TipoFactura": self._get_sii_invoice_type(),
                "ClaveRegimenEspecialOTrascendencia": (self.sii_registration_key.code),
                "DescripcionOperacion": self.sii_description,
                "TipoDesglose": tipo_desglose,
                "ImporteTotal": amount_total,
            }
            if self.thirdparty_invoice:
                inv_dict["FacturaExpedida"]["EmitidaPorTercerosODestinatario"] = "S"
            if self.sii_macrodata:
                inv_dict["FacturaExpedida"].update(Macrodato="S")
            if self.sii_registration_key_additional1:
                inv_dict["FacturaExpedida"].update(
                    {
                        "ClaveRegimenEspecialOTrascendenciaAdicional1": (
                            self.sii_registration_key_additional1.code
                        )
                    }
                )
            if self.sii_registration_key_additional2:
                inv_dict["FacturaExpedida"].update(
                    {
                        "ClaveRegimenEspecialOTrascendenciaAdicional2": (
                            self.sii_registration_key_additional2.code
                        )
                    }
                )
            if "06" in [
                self.sii_registration_key.code,
                self.sii_registration_key_additional1.code,
                self.sii_registration_key_additional2.code,
            ]:
                inv_dict["FacturaExpedida"].update(
                    {"BaseImponibleACoste": self._get_sii_base_cost(tax_lines)}
                )
            if self.sii_registration_key.code in ["12", "13"]:
                inv_dict["FacturaExpedida"]["DatosInmueble"] = {
                    "DetalleInmueble": {
                        "SituacionInmueble": self.sii_property_location,
                        "ReferenciaCatastral": (
                            self.sii_property_cadastrial_code or ""
                        ),
                    }
                }
            exp_dict = inv_dict["FacturaExpedida"]
            if not is_simplified_invoice:
                # Simplified invoices don't have counterpart
                exp_dict["Contraparte"] = {
                    "NombreRazon": partner.name[0:120],
                }
                # Uso condicional de IDOtro/NIF
                exp_dict["Contraparte"].update(self._get_sii_identifier())
            if self.move_type == "out_refund":
                exp_dict["TipoRectificativa"] = self.sii_refund_type
                if self.sii_refund_type == "S":
                    origin = self.refund_invoice_id
                    exp_dict["ImporteRectificacion"] = {
                        "BaseRectificada": abs(origin.amount_untaxed_signed),
                        "CuotaRectificada": abs(
                            origin.amount_total_signed - origin.amount_untaxed_signed
                        ),
                    }
        return inv_dict

    def _get_sii_invoice_dict_in(self, cancel=False):
        """Build dict with data to send to AEAT WS for invoice types:
        in_invoice and in_refund.

        :param cancel: It indicates if the dictionary if for sending a
          cancellation of the invoice.
        :return: invoices (dict) : Dict XML with data for this invoice.
        """
        self.ensure_one()
        invoice_date = self._change_date_format(self.invoice_date)
        reg_date = self._change_date_format(self._get_account_registration_date())
        ejercicio = fields.Date.to_date(self.date).year
        periodo = "%02d" % fields.Date.to_date(self.date).month
        partner = self._sii_get_partner()
        tax_lines = self._get_tax_info()
        (
            desglose_factura,
            tax_amount,
            tax_deductible_amount,
            not_in_amount_total,
        ) = self._get_sii_in_taxes(tax_lines)
        inv_dict = {
            "IDFactura": {
                "IDEmisorFactura": {},
                "NumSerieFacturaEmisor": ((self.ref or "")[:60]),
                "FechaExpedicionFacturaEmisor": invoice_date,
            },
            "PeriodoLiquidacion": {"Ejercicio": ejercicio, "Periodo": periodo},
        }
        # Uso condicional de IDOtro/NIF
        ident = self._get_sii_identifier()
        inv_dict["IDFactura"]["IDEmisorFactura"].update(ident)
        if cancel:
            inv_dict["IDFactura"]["IDEmisorFactura"].update(
                {"NombreRazon": partner.name[0:120]}
            )
        else:
            amount_total = -self.amount_total_signed - not_in_amount_total
            inv_dict["FacturaRecibida"] = {
                # TODO: Incluir los 5 tipos de facturas rectificativas
                "TipoFactura": self._get_sii_invoice_type(),
                "ClaveRegimenEspecialOTrascendencia": self.sii_registration_key.code,
                "DescripcionOperacion": self.sii_description,
                "DesgloseFactura": desglose_factura,
                "Contraparte": {"NombreRazon": partner.name[0:120]},
                "FechaRegContable": reg_date,
                "ImporteTotal": amount_total,
                "CuotaDeducible": tax_deductible_amount,
            }
            if self.sii_macrodata:
                inv_dict["FacturaRecibida"].update(Macrodato="S")
            if self.sii_registration_key_additional1:
                inv_dict["FacturaRecibida"].update(
                    {
                        "ClaveRegimenEspecialOTrascendenciaAdicional1": (
                            self.sii_registration_key_additional1.code
                        )
                    }
                )
            if self.sii_registration_key_additional2:
                inv_dict["FacturaRecibida"].update(
                    {
                        "ClaveRegimenEspecialOTrascendenciaAdicional2": (
                            self.sii_registration_key_additional2.code
                        )
                    }
                )
            if "06" in [
                self.sii_registration_key.code,
                self.sii_registration_key_additional1.code,
                self.sii_registration_key_additional2.code,
            ]:
                inv_dict["FacturaRecibida"].update(
                    {"BaseImponibleACoste": self._get_sii_base_cost(tax_lines)}
                )
            # Uso condicional de IDOtro/NIF
            inv_dict["FacturaRecibida"]["Contraparte"].update(ident)
            if self.move_type == "in_refund":
                rec_dict = inv_dict["FacturaRecibida"]
                rec_dict["TipoRectificativa"] = self.sii_refund_type
                if self.sii_refund_type == "S":
                    refund_tax_amount = self.refund_invoice_id._get_sii_in_taxes(
                        tax_lines
                    )[1]
                    rec_dict["ImporteRectificacion"] = {
                        "BaseRectificada": abs(
                            self.refund_invoice_id.amount_untaxed_signed
                        ),
                        "CuotaRectificada": refund_tax_amount,
                    }
        return inv_dict

    def _get_sii_invoice_dict(self):
        inv_dict = super()._get_sii_invoice_dict()
        round_by_keys(
            inv_dict,
            [
                "BaseImponibleACoste",
            ],
        )
        return inv_dict
