# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

# from odoo.exceptions import ValidationError
from odoo.tools.translate import _

# TODO: This is a workaround, it should be a mixin but Odoo threw the error:
#       Many2many fields AccountTaxTemplate.children_tax_ids and
#           account.tax.template.children_tax_ids use the same table and columns

_logger = logging.getLogger(__name__)


def check_prorate(self):
    for tax in self:
        if tax.prorate:
            if tax.amount_type != "percent":
                _logger.error(
                    _(
                        "On prorate taxes it's only supported "
                        "'percent' as a amount type"
                    )
                )
                # raise ValidationError(
                #     _(
                #         "On prorate taxes it's only supported "
                #         "'percent' as a amount type"
                #     )
                # )
            if tax.type_tax_use != "purchase":
                _logger.error(_("On prorate taxes it's only supported 'purchase' type"))
                # raise ValidationError(
                #     _("On prorate taxes it's only supported 'purchase' type")
                # )
            invoice_tax_positive_repartition_lines = (
                tax.invoice_repartition_line_ids.filtered(
                    lambda x: x.repartition_type == "tax" and x.factor_percent > 0
                )
            )
            refund_tax_positive_repartition_lines = (
                tax.refund_repartition_line_ids.filtered(
                    lambda x: x.repartition_type == "tax" and x.factor_percent > 0
                )
            )
            if (
                len(invoice_tax_positive_repartition_lines) != 2
                or len(refund_tax_positive_repartition_lines) != 2
            ):
                _logger.error(
                    _("On prorate taxes it's only supported two tax repartition lines")
                )
                # raise ValidationError(
                #     _(
                #         "On prorate taxes it's only supported "
                #         "two tax repartition lines"
                #     )
                # )
