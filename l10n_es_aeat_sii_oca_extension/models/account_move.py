# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.l10n_es_aeat_sii_oca.models.account_move import round_by_keys


def sum_key(elem, key):
    value = 0
    if isinstance(elem, (list, tuple)):
        for v in elem:
            value += sum_key(v, key)
    elif isinstance(elem, dict):
        for k, v in elem.items():
            value += v if k == key else sum_key(v, key)
    return value


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_sii_in_taxes_deductible(self):
        self.ensure_one()
        taxes_sfrs = self._get_sii_taxes_map(["SFRS"])
        taxes_sfrisp = self._get_sii_taxes_map(["SFRISP"])
        tax_deductible_amount = 0.0
        tax_lines = self._get_aeat_tax_info()
        for tax_line in tax_lines.values():
            tax = tax_line["tax"]
            if tax in taxes_sfrisp + taxes_sfrs:
                tax_deductible_amount += tax_line["actual_deductible_amount"]
        return tax_deductible_amount

    def _get_sii_invoice_dict_in(self, cancel=False):
        inv_dict = super()._get_sii_invoice_dict_in(cancel=cancel)
        if not cancel:
            inv_dict["FacturaRecibida"][
                "CuotaDeducible"
            ] = self._get_sii_in_taxes_deductible()
            if "06" in (
                self.sii_registration_key.code,
                self.sii_registration_key_additional1.code,
                self.sii_registration_key_additional2.code,
            ):
                inv_dict["FacturaRecibida"]["BaseImponibleACoste"] = sum_key(
                    inv_dict["FacturaRecibida"]["DesgloseFactura"],
                    "BaseImponible",
                )
        return inv_dict

    def _get_sii_invoice_dict_out(self, cancel=False):
        inv_dict = super()._get_sii_invoice_dict_out(cancel=cancel)
        if not cancel:
            if "06" in (
                self.sii_registration_key.code,
                self.sii_registration_key_additional1.code,
                self.sii_registration_key_additional2.code,
            ):
                inv_dict["FacturaExpedida"]["BaseImponibleACoste"] = sum_key(
                    inv_dict["FacturaExpedida"]["TipoDesglose"], "BaseImponible"
                )
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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _process_aeat_tax_base_info(self, res, tax, sign):
        super()._process_aeat_tax_base_info(res, tax, sign)
        for tax in res.keys():
            res[tax].setdefault("actual_deductible_amount", 0)

    def _process_aeat_tax_fee_info(self, res, tax, sign):
        super()._process_aeat_tax_fee_info(res, tax, sign)
        res[tax].setdefault("atual_deductible_amount", 0)
        if self.tax_repartition_line_id.account_id:
            res[tax]["actual_deductible_amount"] += self.balance * sign
