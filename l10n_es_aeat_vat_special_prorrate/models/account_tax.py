# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountTax(models.Model):
    _inherit = "account.tax"

    def compute_all(
        self,
        price_unit,
        currency=None,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
        handle_price_include=True,
        include_caba_tags=False,
        rounding_method=None,
    ):
        res = super().compute_all(
            price_unit,
            currency=currency,
            quantity=quantity,
            product=product,
            partner=partner,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=include_caba_tags,
            rounding_method=rounding_method,
        )
        # group repartition lines by tax
        # Sort the taxes so that those without account_id come last. This is
        # to have an Odoo like behavior when no rounding errors occur.
        sorted_taxes = sorted(
            res["taxes"], key=lambda x: x["account_id"] in (None, False)
        )
        rlines_by_tax = {}
        for tax in sorted_taxes:
            rline = self.env["account.tax.repartition.line"].browse(
                tax["tax_repartition_line_id"]
            )
            if rline and rline.tax_id.prorate:
                rline_type = rline.document_type
                if rline.repartition_type == "tax" and rline.factor_percent == 100.0:
                    rlines_by_tax.setdefault((rline_type, rline.tax_id), []).append(tax)
        # round the prorate pairs for each tax
        for (rltype, tax), prorate_taxes in rlines_by_tax.items():
            # Defensive check: constraint on account.tax should guarantee exactly
            # 2 with 100% but protect against data corruption since we're gonna
            # index this list.
            if len(prorate_taxes) != 2:
                raise ValidationError(
                    _(
                        "Runtime error: Prorate tax '%(tax_name)s' "
                        "has %(lines_count)i %(rltype)s repartition "
                        "lines instead of expected 2. This may indicate "
                        "data corruption or constraint bypass."
                    )
                    % {
                        "tax_name": tax.name,
                        "lines_count": len(prorate_taxes),
                        "rltype": rltype,
                    }
                )
            base_tax_amount = sum(x["amount"] for x in prorate_taxes)
            prorate_taxes[0]["amount"] = currency.round(prorate_taxes[0]["amount"])
            prorate_taxes[1]["amount"] = base_tax_amount - prorate_taxes[0]["amount"]
        return res

    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(record, **kwargs)
        res["prorate_year"] = self._get_base_line_field_value_from_record(
            record, "prorate_year", kwargs, 0
        )
        return res

    def _prepare_tax_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_tax_line_for_taxes_computation(record, **kwargs)
        res["prorate_year"] = self._get_base_line_field_value_from_record(
            record, "prorate_year", kwargs, 0
        )
        return res

    def _prepare_base_line_grouping_key(self, base_line):
        res = super()._prepare_base_line_grouping_key(base_line)
        res["prorate_year"] = base_line["prorate_year"]
        return res

    def _prepare_tax_line_repartition_grouping_key(self, tax_line):
        res = super()._prepare_tax_line_repartition_grouping_key(tax_line)
        res["prorate_year"] = tax_line["prorate_year"]
        return res
