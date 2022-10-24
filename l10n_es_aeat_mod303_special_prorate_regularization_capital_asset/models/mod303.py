# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    field_43 = fields.Float(
        string="[43] Capital Assets Prorate Regularization",
        default=0,
        compute="_compute_field_43",
        states={"done": [("readonly", True)]},
        help="Capital assets regularization by application of the final percentage.",
    )

    @api.depends("tax_line_ids", "tax_line_ids.amount")
    def _compute_field_43(self):
        for report in self:
            report.field_43 = report.tax_line_ids.filtered(
                lambda x: x.field_number == 43
            ).amount

    def _default_counterpart_capital_assets_receivable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6392")
        )

    counterpart_capital_assets_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Counterpart Capital Assets Account Receivable",
        default=_default_counterpart_capital_assets_receivable_account_id,
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_capital_assets_payable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6342")
        )

    counterpart_capital_assets_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        default=_default_counterpart_capital_assets_payable_account_id,
        string="Counterpart Capital Assets Payable Account",
        domain="[('company_id', '=', company_id)]",
    )

    def _calculate_repartition_tax(self, asset):
        if asset.move_id.move_type not in ("in_invoice", "in_refund"):
            raise ValidationError(
                _(
                    "Account entry related to the asset "
                    "is neither an invoice nor a refund"
                )
            )
        repartition_lines = (
            asset.prorate_tax_id.invoice_repartition_line_ids
            if asset.move_id.move_type == "in_invoice"
            else asset.prorate_tax_id.refund_repartition_line_ids
        )
        taxes = repartition_lines.filtered(
            lambda x: x.account_id and x.repartition_type == "tax"
        )
        if len(taxes) == 0:
            raise ValidationError(
                _("Repartition line not found on asset %s tax %s")
                % (asset.id, asset.prorate_tax_id)
            )
        if len(taxes) > 1:
            raise ValidationError(
                _("More than one repartition line found on asset %s tax %s")
                % (asset.id, asset.prorate_tax_id)
            )
        return taxes

    def _process_tax_line_regularization_prorate_capital_asset(self, tax_lines):
        self.ensure_one()
        groups = []
        for tax_line in tax_lines:
            groups += self.env["account.move.line"].read_group(
                [
                    ("id", "in", tax_line.move_line_ids.ids),
                    ("parent_state", "=", "posted"),
                ],
                ["account_id", "name", "asset_id", "debit", "credit"],
                ["account_id", "name", "asset_id"],
                lazy=False,
            )
        lines = []
        prorate_year = self._get_prorate_year(self.company_id, self.year)
        precision = self.env["decimal.precision"].precision_get("Account")
        for group in groups:
            asset = self.env["account.asset"].browse(group["asset_id"][0])
            percent_diff = (
                asset.final_prorate_percent - prorate_year.tax_final_percentage
            )
            repartition_tax = self._calculate_repartition_tax(asset)
            new_balance = round(
                (asset.tax_total_amount / asset.capital_asset_type_id.period)
                * percent_diff
                / 100,
                precision,
            )
            group["account_id"] = (
                repartition_tax.account_id.id,
                repartition_tax.account_id.name,
            )
            if new_balance:
                group["debit"] = new_balance if new_balance > 0 else 0
                group["credit"] = -new_balance if new_balance < 0 else 0
                line = self._prepare_regularization_move_line(group)
                line["asset_id"] = group["asset_id"][0]
                lines.append(line)
        return lines

    # TODO: It's necessary this hook?
    def _retrieve_assets(self, move_lines):
        return move_lines.mapped("asset_id")

    def _prepare_tax_line_vals(self, map_line):
        self.ensure_one()
        res = super()._prepare_tax_line_vals(map_line)
        if self.period_type not in ("4T", "12"):
            if map_line.field_number == 44:
                res["amount"] = 0
                res["move_line_ids"] = False
            return res
        else:
            if map_line.field_number == 43:
                res = self._prepare_tax_line_vals_dates(
                    datetime.date(
                        self.year
                        - self.env[
                            "l10n.es.account.capital.asset.type"
                        ]._get_max_period(),
                        1,
                        1,
                    ),
                    datetime.date(self.year, 12, 31),
                    map_line,
                )
                move_lines = self.env["account.move.line"].browse(
                    res["move_line_ids"][0][2]
                )
                move_lines_no_asset = move_lines.filtered(lambda x: not x.asset_id)
                if move_lines_no_asset:
                    raise ValidationError(
                        _(
                            "The following invoices %s have products with "
                            "capital asset taxes but without asset"
                        )
                        % move_lines_no_asset.mapped("move_id.display_name")
                    )
                prorate_year = self._get_prorate_year(self.company_id, self.year)
                assets_to_update = move_lines.mapped("asset_id").filtered(
                    lambda x: x.capital_asset_type_id and x.date_start.year == self.year
                )
                assets_to_update.final_prorate_percent = (
                    prorate_year.tax_final_percentage
                )
                prorate_max_diff = float(
                    self.env["ir.config_parameter"].get_param(
                        "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset."
                        "capital_asset_prorate_max_diff"
                    )
                )
                assets_to_regularize = self._retrieve_assets(move_lines).filtered(
                    lambda x: all(
                        [
                            x.capital_asset_type_id,
                            x.state == "open",
                            x.date_start,
                            x.date_start.year < self.year,
                            x.date_start.year
                            >= self.year - x.capital_asset_type_id.period,
                            abs(
                                prorate_year.tax_final_percentage
                                - x.final_prorate_percent
                            )
                            > prorate_max_diff,
                        ]
                    )
                )
                move_line_ids = []
                amount = 0
                precision = self.env["decimal.precision"].precision_get("Account")
                for asset in assets_to_regularize:
                    asset_amount = 0
                    percent_diff = (
                        prorate_year.tax_final_percentage - asset.final_prorate_percent
                    )
                    # TODO treure move_line_id
                    if asset.invoice_move_line:
                        move_line_ids.append(asset.invoice_move_line.id)
                    asset_amount += round(
                        (asset.tax_total_amount / asset.capital_asset_type_id.period)
                        * percent_diff
                        / 100,
                        precision,
                    )
                    asset_regularization_line = (
                        asset.capital_asset_prorate_regularization_ids._get_by_year(
                            self
                        )
                    )
                    if asset_regularization_line:
                        # if not asset_regularization_line.mod303_id:
                        #     raise ValidationError(
                        #         _(
                        #             "This asset have a prorate regularization"
                        #             " line this year: %s, but it's not related"
                        #             " with a model 303. Please, review prorate"
                        #             " regularizations of capital asset: %s"
                        #         )
                        #         % (self.year, asset.name)
                        #     )
                        # elif asset_regularization_line.mod303_id != self:
                        #     raise ValidationError(
                        #         _(
                        #             "This asset have a prorate regularization"
                        #             " line this year: %s,"
                        #             " but related with another model 303. "
                        #             "Please, review prorate regularizations "
                        #             "of capital asset: %s"
                        #         )
                        #         % (self.year, asset.name)
                        #     )
                        # else:
                        asset_regularization_line.amount = asset_amount

                    else:
                        asset["capital_asset_prorate_regularization_ids"] = [
                            (
                                0,
                                0,
                                {
                                    "year": self.year,
                                    "amount": asset_amount,
                                    "prorate_year": prorate_year.tax_final_percentage,
                                    "mod303_id": self.id,
                                },
                            )
                        ]
                    amount += asset_amount
                res["amount"] = amount
                res["move_line_ids"] = [(6, 0, move_line_ids)]
        return res

    def create_regularization_move(self):
        super().create_regularization_move()
        if self.period_type in ("4T", "12"):
            if any(
                [
                    not self.counterpart_capital_assets_receivable_account_id,
                    not self.counterpart_capital_assets_payable_account_id,
                    not self.journal_id,
                ]
            ):
                raise UserError(
                    _(
                        "You must fill both journal and counterpart receivable/payable account."
                    )
                )
            self.create_regularization_move_prorate_capital_asset()

    def create_regularization_move_prorate_capital_asset(self):
        self.ensure_one()
        move_vals = self._prepare_move_vals()
        line_vals_list = self._prepare_regularization_move_lines_prorate_capital_asset()
        move_vals["line_ids"] = [(0, 0, x) for x in line_vals_list]
        if line_vals_list:
            if self.move_prorate_capital_asset_id:
                raise ValidationError(
                    _("The account move cannot be created because it already exists")
                )
            self.move_prorate_capital_asset_id = (
                self.env["account.move"]
                .with_context(allow_asset=True)
                .create(move_vals)
            )

    def _prepare_regularization_move_lines_prorate_capital_asset(self):
        lines = self._process_tax_line_regularization_prorate_capital_asset(
            self.tax_line_ids.filtered(lambda x: x.field_number == 43)
        )
        asset_counterpart = []
        for line in lines:
            account = (
                self.counterpart_capital_assets_receivable_account_id
                if line["credit"] - line["debit"] < 0
                else self.counterpart_capital_assets_payable_account_id
            )
            regularize_line = self._prepare_counterpart_move_line(
                account, line["debit"], line["credit"]
            )
            regularize_line["name"] = "Capital Asset Prorate Regularization"
            regularize_line["asset_id"] = line["asset_id"]
            asset_counterpart.append(regularize_line)
        for counterpart in asset_counterpart:
            lines.append(counterpart)
        return lines
