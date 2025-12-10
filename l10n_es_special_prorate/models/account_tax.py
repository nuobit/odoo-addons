# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    prorate = fields.Boolean()

    @api.constrains(
        "prorate",
        "amount_type",
        "type_tax_use",
        "invoice_repartition_line_ids",
        "refund_repartition_line_ids",
    )
    def _check_prorate(self):
        for tax in self:
            if tax.prorate:
                if tax.amount_type != "percent":
                    raise ValidationError(
                        _(
                            "On prorate taxes it's only supported "
                            "'percent' as a amount type"
                        )
                    )
                if tax.type_tax_use != "purchase":
                    raise ValidationError(
                        _("On prorate taxes it's only supported 'purchase' type")
                    )
                all_repartition_lines = [
                    ("invoice", tax.invoice_repartition_line_ids),
                    ("refund", tax.refund_repartition_line_ids),
                ]
                for rltype, rlines in all_repartition_lines:
                    valid_rlines = rlines.filtered(
                        lambda x: x.repartition_type == "tax"
                        and x.factor_percent == 100.0
                    )
                    if len(valid_rlines) != 2:
                        raise ValidationError(
                            _(
                                "Prorate tax '%(tax_name)s' requires exactly "
                                "two 100%% positive tax "
                                "repartition lines (found %(found_count)i). "
                                "Please check the configuration "
                                "of the %(repartition_type)s repartition "
                                "lines of this tax."
                            )
                            % {
                                "tax_name": tax.name,
                                "found_count": len(valid_rlines),
                                "repartition_type": rltype,
                            }
                        )

    @api.model
    def prorate_context(self, record, date, company):
        if not date:
            date_norm = fields.Date.context_today(record)
        else:
            if isinstance(date, datetime.date):
                date_norm = date
            elif isinstance(date, datetime.datetime):
                date_norm = fields.Date.context_today(record, date)
            else:
                raise ValidationError(
                    _("Invalid date format '%s' for prorate context") % date
                )
        return {
            "prorate": (
                fields.Date.to_string(date_norm),
                company.id,
            )
        }

    def get_non_deductible_percent(self, date, company, is_refund):
        repartition_field = (
            is_refund
            and "refund_repartition_line_ids"
            or "invoice_repartition_line_ids"
        )
        value = 0
        for rec in self:
            if rec.amount_type == "percent":
                non_deductible_rep_line = rec.mapped(repartition_field).filtered(
                    lambda x: x.repartition_type == "tax"
                    and x.factor_percent > 0
                    and not x.account_id
                )
                if non_deductible_rep_line:
                    if len(non_deductible_rep_line) > 1:
                        raise ValidationError(
                            _(
                                "On non deductible taxes there should be only "
                                "one repartition line without account"
                            )
                        )
                    context = {}
                    if rec.prorate:
                        context = self.prorate_context(rec, date, company)
                    value += (
                        rec.amount
                        * non_deductible_rep_line.with_context(**context).factor
                    )
            elif rec.amount_type == "group":
                for tax_child in rec.children_tax_ids:
                    value += tax_child.get_non_deductible_percent(
                        date, company, is_refund
                    )
            else:
                raise NotImplementedError(
                    _("Tax type '%(amount_type)s' not supported yet")
                    % {"amount_type": rec.amount_type}
                )
        return value
