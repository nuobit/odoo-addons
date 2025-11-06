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
        rlines_by_tax = {}
        for tax in sorted(
            res["taxes"], key=lambda x: x["account_id"] or 0, reverse=True
        ):
            rline = self.env["account.tax.repartition.line"].browse(
                tax["tax_repartition_line_id"]
            )
            if rline and rline.tax_id.prorate:
                if rline.repartition_type == "tax" and rline.factor_percent > 0:
                    rlines_by_tax.setdefault(rline.tax_id, []).append(tax)
        # round the prorate pairs for each tax
        for tax, prorate_taxes in rlines_by_tax.items():
            if len(prorate_taxes) != 2:
                raise ValidationError(
                    _(
                        "Prorate tax '%s' requires exactly two positive tax repartition "
                        "lines (found %s). On prorate taxes it's only supported two "
                        "positive tax repartition lines"
                    )
                    % (tax.name, len(prorate_taxes))
                )
            base_tax_amount = sum(x["amount"] for x in prorate_taxes)
            prorate_taxes[0]["amount"] = currency.round(prorate_taxes[0]["amount"])
            prorate_taxes[1]["amount"] = base_tax_amount - prorate_taxes[0]["amount"]
        return res
