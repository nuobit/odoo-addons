# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountTax(models.Model):
    _inherit = "account.tax"

    prorrate_type = fields.Selection(
        selection=[
            ("deductible", _("Deductible")),
            ("non-deductible", _("Non-deductible")),
        ],
        string="Prorrate type",
    )

    def get_prorrate_ratio(self, date, company_id):
        date = date or fields.Date.context_today(self)

        prorrate_map = self.env["aeat.map.special.prorrate.year"].search(
            [
                ("company_id", "=", company_id),
                ("year", "=", fields.Date.from_string(date).year),
            ]
        )
        if not prorrate_map:
            raise ValidationError(
                _("If a tax has prorrate the year should exist on vat mapping")
            )

        prorrate_ratio = prorrate_map.tax_percentage / 100
        if self.prorrate_type == "non-deductible":
            prorrate_ratio = 1 - prorrate_ratio

        return prorrate_ratio

    def get_non_deductible_percent(self, date, company_id):
        value = 0
        for rec in self:
            if rec.amount_type == "percent":
                if not any(
                    rec.invoice_repartition_line_ids.mapped("account_id")
                    + rec.refund_repartition_line_ids.mapped("account_id")
                ):
                    tax_percent = rec.amount
                    if rec.prorrate_type:
                        tax_percent *= rec.get_prorrate_ratio(date, company_id)
                    value += tax_percent
            elif rec.amount_type == "group":
                for tax_child in rec.children_tax_ids:
                    value += tax_child.get_non_deductible_percent(date, company_id)
            else:
                raise NotImplementedError(
                    "Tax type '%s' not suported yet" % rec.amount_type
                )

        return value

    @api.constrains("prorrate_type", "amount_type", "price_include")
    def _check_prorrate(self):
        for tax in self:
            if tax.prorrate_type:
                if tax.amount_type != "percent" or tax.price_include:
                    raise ValidationError(
                        _(
                            "If a tax has prorrate, it's only suported 'percent' type "
                            "with price not included"
                        )
                    )

                parent_ids = tax.env["account.tax"].search(
                    [("children_tax_ids", "=", tax.id)]
                )
                for parent_id in parent_ids:
                    sibling_dup = parent_id.children_tax_ids.filtered(
                        lambda x: x.id != tax.id
                        and x.prorrate_type == tax.prorrate_type
                    )
                    if sibling_dup:
                        raise ValidationError(
                            _(
                                "Multiple taxes with the same prorrate type "
                                "under same parent is not suported"
                            )
                        )
