# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError, ValidationError

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


def merge_nested_dicts(target_dict, source_dict, key_funcs=None, path=None, level=0):
    def get_path_value(data, path):
        for key in path:
            data = data[key]
        return data

    def set_path_value(data, path, value):
        for key in path[:-1]:
            data = data[key]
        data[path[-1]] = value

    def path_exists(data, path):
        for key in path:
            if key not in data:
                return False
            data = data[key]
        return True

    if key_funcs is None:
        key_funcs = {}
    if path is None:
        path = []
    if isinstance(source_dict, (str, int, float, bool)):
        if get_path_value(target_dict, path) != source_dict:
            raise ValidationError(
                _("SII data merge error: No match at path %s: %s != %s")
                % (path, get_path_value(target_dict, path), source_dict)
            )
    elif isinstance(source_dict, dict):
        for key, value in source_dict.items():
            new_path = path + [key]
            if path_exists(target_dict, new_path):
                if key in key_funcs:
                    func = key_funcs[key]
                    existing_value = get_path_value(target_dict, new_path)
                    merged_value = func(existing_value, source_dict[key])
                    set_path_value(target_dict, new_path, merged_value)
                else:
                    merge_nested_dicts(
                        target_dict,
                        value,
                        key_funcs=key_funcs,
                        path=new_path,
                        level=level + 1,
                    )
            else:
                set_path_value(target_dict, new_path, value)
    else:
        raise UserError(
            _("SII data merge error: Unsupported type: %s: %s")
            % (type(source_dict), source_dict)
        )


def merge_detalle_iva(tax_details_list1, tax_details_list2):
    """Merge tax details (DetalleIVA) by grouping and summing by TipoImpositivo."""
    merged_by_rate = {}
    rate_key = "TipoImpositivo"

    for tax_detail in tax_details_list1 + tax_details_list2:
        if rate_key not in tax_detail:
            raise ValidationError(
                _("SII tax detail merge error: Missing '%s' key in %s")
                % (rate_key, tax_detail)
            )
        tax_detail = dict(tax_detail)
        tax_rate = tax_detail.pop(rate_key)

        if tax_rate not in merged_by_rate:
            merged_by_rate[tax_rate] = tax_detail
        else:
            for key, value in tax_detail.items():
                if key not in merged_by_rate[tax_rate]:
                    raise ValidationError(
                        _("SII tax detail merge error: Missing '%s' key in %s")
                        % (key, merged_by_rate[tax_rate])
                    )
                merged_by_rate[tax_rate][key] += value

    result_list = []
    for tax_rate, tax_data in merged_by_rate.items():
        result_list.append(
            {
                rate_key: tax_rate,
                **tax_data,
            }
        )
    return result_list


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

    def _get_sii_out_taxes(self):
        tipo_desglose, not_in_amount_total = super()._get_sii_out_taxes()
        if "06" in (
            self.sii_registration_key.code,
            self.sii_registration_key_additional1.code,
            self.sii_registration_key_additional2.code,
        ):
            if "DesgloseTipoOperacion" in tipo_desglose:
                operation_types = list(tipo_desglose["DesgloseTipoOperacion"].values())
                merged_data = operation_types[0]
                for operation_type in operation_types[1:]:
                    merge_nested_dicts(
                        merged_data, operation_type, {"DetalleIVA": merge_detalle_iva}
                    )
                tipo_desglose = {"DesgloseFactura": merged_data}
        return tipo_desglose, not_in_amount_total

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
        res[tax].setdefault("actual_deductible_amount", 0)
        if self.tax_repartition_line_id.account_id:
            res[tax]["actual_deductible_amount"] += self.balance * sign
