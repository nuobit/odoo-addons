# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    field_44 = fields.Float(
        string="[44] Prorate Regularization",
        default=0,
        compute="_compute_field_44",
        states={"done": [("readonly", True)]},
        help="Prorate regularization by application of the final percentage.",
    )

    @api.depends("tax_line_ids", "tax_line_ids.amount")
    def _compute_field_44(self):
        for report in self:
            report.field_44 = report.tax_line_ids.filtered(
                lambda x: x.field_number == 44
            ).amount

    def _default_counterpart_prorate_receivable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6391")
        )

    counterpart_prorate_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Counterpart Prorate Account Receivable",
        default=_default_counterpart_prorate_receivable_account_id,
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_prorate_payable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6341")
        )

    counterpart_prorate_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        default=_default_counterpart_prorate_payable_account_id,
        string="Counterpart Prorate Payable Account",
        domain="[('company_id', '=', company_id)]",
    )

    def _process_tax_line_regularization_prorate(self, tax_lines):
        self.ensure_one()
        groups = []
        for tax_line in tax_lines:
            groups += self.env["account.move.line"].read_group(
                [
                    ("id", "in", tax_line.move_line_ids.ids),
                    ("parent_state", "=", "posted"),
                ],
                ["account_id", "tax_line_id", "debit", "credit"],
                ["account_id", "tax_line_id"],
                lazy=False,
            )

        lines = []
        prorate_year = self._get_prorate_year(self.company_id, self.year)
        precision = self.env["decimal.precision"].precision_get("Account")
        for group in groups:
            old_balance = group["debit"] - group["credit"]
            new_balance = round(
                old_balance
                * (1 - prorate_year.tax_final_percentage / prorate_year.tax_percentage),
                precision,
            )
            # prorate
            if new_balance:
                group["debit"] = new_balance if new_balance > 0 else 0
                group["credit"] = -new_balance if new_balance < 0 else 0
                line = self._prepare_regularization_move_line(group)
                line["tax_line_id"] = group["tax_line_id"][0]
                lines.append(line)
        return lines

    def _prepare_tax_line_vals(self, map_line):
        self.ensure_one()
        res = super()._prepare_tax_line_vals(map_line)
        if self.period_type not in ("4T", "12"):
            if map_line.field_number == 44:
                res["amount"] = 0
                res["move_line_ids"] = False
            return res
        else:
            if map_line.field_number == 44:
                res = self._prepare_tax_line_vals_dates(
                    datetime.date(self.year, 1, 1),
                    datetime.date(self.year, 12, 31),
                    map_line,
                )
                prorate_year = self._get_prorate_year(self.company_id, self.year)
                self.env["decimal.precision"].precision_get("Account")
                # tax_base_amount = 0
                # for move_line in self.env['account.move.line']
                # .browse(res["move_line_ids"][0][2]):
                #     sign = 1 if move_line.move_id.move_type == "in_invoice" else -1
                #     tax_base_amount += round(move_line.tax_base_amount *
                #     move_line.tax_line_id.amount / 100 * sign,
                #                              precision)
                #
                # amount = tax_base_amount * prorate_year.tax_percentage / 100
                # TODO: bug--> if tax_final_percentage or
                #  tax_percentage are 0 --> error.  REMOVE THIS LINE AND FLOAT COMPARE!
                res["amount"] = res["amount"] * (
                    1 - prorate_year.tax_final_percentage / prorate_year.tax_percentage
                )
                # if not float_compare(amount_test, amount, precision_rounding=precision):
                #     raise ValidationError(_("FAIL"))
                # TODO: UNTIL HERE
        return res

    def create_regularization_move(self):
        super().create_regularization_move()
        if self.period_type in ("4T", "12"):
            if any(
                [
                    not self.counterpart_prorate_receivable_account_id,
                    not self.counterpart_prorate_payable_account_id,
                    not self.journal_id,
                ]
            ):
                raise UserError(
                    _(
                        "You must fill both journal and counterpart "
                        "receivable/payable account."
                    )
                )
            self.create_regularization_move_prorate()

    def create_regularization_move_prorate(self):
        self.ensure_one()
        move_vals = self._prepare_move_vals()
        line_vals_list = self._prepare_regularization_move_lines_prorate()
        move_vals["line_ids"] = [(0, 0, x) for x in line_vals_list]
        if line_vals_list:
            if self.move_prorate_id:
                raise ValidationError(
                    _("The account move cannot be created because it already exists")
                )
            self.move_prorate_id = self.env["account.move"].create(move_vals)

    def _prepare_regularization_move_lines_prorate(self):
        self.ensure_one()
        # Compute regular lines
        lines = self._process_tax_line_regularization_prorate(
            self.tax_line_ids.filtered(lambda x: x.field_number == 44)
        )
        # Compute counterpart lines
        debit = sum(x["debit"] for x in lines)
        credit = sum(x["credit"] for x in lines)
        account = (
            self.counterpart_prorate_receivable_account_id
            if credit - debit < 0
            else self.counterpart_prorate_payable_account_id
        )
        regularize_line = self._prepare_counterpart_move_line(account, debit, credit)
        regularize_line["name"] = "Prorate Regularization"
        lines.append(regularize_line)
        return lines
