# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tools.translate import _

# TODO: This is a workaround, it should be a mixin but Odoo threw the error:
#       Many2many fields AccountTaxTemplate.children_tax_ids and
#           account.tax.template.children_tax_ids use the same table and columns


def check_prorate(self):
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
                    lambda x: x.repartition_type == "tax" and x.factor_percent == 100.0
                )
                if len(valid_rlines) != 2:
                    raise ValidationError(
                        _(
                            "Prorate tax '%s' requires exactly two 100%% positive tax "
                            "repartition lines (found %i). Please check the configuration "
                            "of the %s repartition lines of this tax."
                        )
                        % (tax.name, len(valid_rlines), rltype)
                    )
