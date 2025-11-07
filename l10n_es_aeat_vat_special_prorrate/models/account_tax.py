# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
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
    ):
        res = super().compute_all(
            price_unit,
            currency=currency,
            quantity=quantity,
            product=product,
            partner=partner,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
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
                rline_type = "invoice" if rline.invoice_tax_id else "refund"
                if rline.repartition_type == "tax" and rline.factor_percent == 100.0:
                    rlines_by_tax.setdefault((rline_type, rline.tax_id), []).append(tax)
        # round the prorate pairs for each tax
        for (rltype, tax), prorate_taxes in rlines_by_tax.items():
            # Defensive check: constraint on account.tax should guarantee exactly 2 with
            # 100% but protect against data corruption since we're gonna index this list.
            if len(prorate_taxes) != 2:
                raise ValidationError(
                    _(
                        "Runtime error: Prorate tax '%s' has %i %s repartition "
                        "lines instead of expected 2. This may indicate data "
                        "corruption or constraint bypass."
                    )
                    % (tax.name, len(prorate_taxes), rltype)
                )
            base_tax_amount = sum(x["amount"] for x in prorate_taxes)
            prorate_taxes[0]["amount"] = currency.round(prorate_taxes[0]["amount"])
            prorate_taxes[1]["amount"] = base_tax_amount - prorate_taxes[0]["amount"]
        return res
