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
        "repartition_line_ids",
    )
    def _check_prorate(self):
        for tax in self:
            if not tax.prorate:
                continue
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
            for doc_type in ("invoice", "refund"):
                rlines = tax.repartition_line_ids.filtered(
                    lambda x, dt=doc_type: x.document_type == dt
                    and x.repartition_type == "tax"
                    and x.factor_percent == 100.0
                )
                if len(rlines) != 2:
                    raise ValidationError(
                        _(
                            "Prorate tax '%(tax_name)s' requires exactly "
                            "two 100%% positive tax "
                            "repartition lines (found %(found_count)i). "
                            "Please check the configuration "
                            "of the %(repartition_type)s repartition "
                            "lines of this tax.",
                            tax_name=tax.name,
                            found_count=len(rlines),
                            repartition_type=doc_type,
                        )
                    )

    @api.constrains(
        "invoice_repartition_line_ids",
        "refund_repartition_line_ids",
        "repartition_line_ids",
    )
    def _validate_repartition_lines(self):
        non_prorate = self.filtered(lambda r: not r.prorate)
        if non_prorate:
            super(AccountTax, non_prorate)._validate_repartition_lines()
        prorate = self.filtered("prorate")
        for record in prorate:
            invoice_reps = record.repartition_line_ids.filtered(
                lambda ln: ln.document_type == "invoice"
            ).sorted(lambda ln: (ln.sequence, ln.id))
            refund_reps = record.repartition_line_ids.filtered(
                lambda ln: ln.document_type == "refund"
            ).sorted(lambda ln: (ln.sequence, ln.id))
            if (
                record.amount_type == "group"
                and not invoice_reps
                and not refund_reps
            ):
                continue
            record._check_repartition_lines(invoice_reps)
            record._check_repartition_lines(refund_reps)
            if len(invoice_reps) != len(refund_reps):
                raise ValidationError(
                    _(
                        "Invoice and credit note distribution "
                        "should have the same number of lines."
                    )
                )
            if not invoice_reps.filtered(
                lambda x: x.repartition_type == "tax"
            ) or not refund_reps.filtered(
                lambda x: x.repartition_type == "tax"
            ):
                raise ValidationError(
                    _(
                        "Invoice and credit note repartition should "
                        "have at least one tax repartition line."
                    )
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
                    _("Invalid date format '%(date)s' for prorate context",
                        date=date)
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
                    _(
                        "Tax type '%(amount_type)s' not supported yet",
                        amount_type=rec.amount_type,
                    )
                )
        return value
