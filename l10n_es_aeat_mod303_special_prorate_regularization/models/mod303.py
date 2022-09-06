# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class L10nEsAeatMapTaxLine(models.Model):
    _inherit = "l10n.es.aeat.map.tax.line"

    to_regularize_prorate = fields.Boolean(
        default=False, string="To Regularize Prorata"
    )


class L10nEsAeatTaxLine(models.Model):
    _inherit = "l10n.es.aeat.tax.line"

    to_regularize_prorate = fields.Boolean(
        related="map_line_id.to_regularize_prorate", readonly=True
    )


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
            self.env.ref("l10n_es.account_common_6341")
        )

    counterpart_prorate_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Counterpart Prorate Account Receivable",
        default=_default_counterpart_prorate_receivable_account_id,
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_prorate_payable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6391")
        )

    counterpart_prorate_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        default=_default_counterpart_prorate_payable_account_id,
        string="Counterpart Prorate Payable Account",
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_capital_assets_receivable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6342")
        )

    counterpart_capital_assets_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Counterpart Capital Assets Account Receivable",
        default=_default_counterpart_capital_assets_receivable_account_id,
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_capital_assets_payable_account_id(self):
        return self.get_account_from_template(
            self.env.ref("l10n_es.account_common_6392")
        )

    counterpart_capital_assets_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        default=_default_counterpart_capital_assets_payable_account_id,
        string="Counterpart Capital Assets Payable Account",
        domain="[('company_id', '=', company_id)]",
    )

    def _process_tax_line_regularization_prorate(self, tax_lines):
        self.ensure_one()
        groups = self.env["account.move.line"].read_group(
            [
                ("id", "in", tax_lines.move_line_ids.ids),
                ("parent_state", "=", "posted"),
            ],
            ["account_id", "tax_line_id", "debit", "credit"],
            ["account_id", "tax_line_id"],
            lazy=False,
        )
        lines = []
        prorate_line = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
            self.company_id.id, self.year
        )
        if prorate_line.state not in ("closed", "finale"):
            raise ValidationError(_("Prorrate year is not closed"))
        precision = self.env["decimal.precision"].precision_get("Account")
        for group in groups:
            old_balance = group["debit"] - group["credit"]
            new_balance = round(
                old_balance
                * (1 - prorate_line.tax_final_percentage / prorate_line.tax_percentage),
                precision,
            )
            if new_balance:
                group["debit"] = new_balance if new_balance > 0 else 0
                group["credit"] = -new_balance if new_balance < 0 else 0
                lines.append(self._prepare_regularization_move_line_prorate(group))
        return lines

    @api.model
    def _prepare_regularization_move_line_prorate(self, account_group):
        return {
            **self._prepare_regularization_move_line(account_group),
            "tax_line_id": account_group["tax_line_id"][0],
        }

    def _prepare_tax_line_vals(self, map_line):
        self.ensure_one()
        if map_line.field_number == 43:
            a = 1
        res = super()._prepare_tax_line_vals(map_line)
        if self.period_type not in ("4T", "12"):
            if map_line.field_number in (43, 44):
                res["amount"] = 0
                res["move_line_ids"] = False
            return res
        else:
            # TODO: Create methods for each field number.
            if map_line.field_number == 44:
                date_values = {
                    "date_start": "%s-01-01" % self.year,
                    "date_end": "%s-12-31" % self.year
                }
                res = super(L10nEsAeatMod303Report,
                            self.new(self.copy_data(default=date_values)[0]))._prepare_tax_line_vals(
                    map_line)
                res["res_id"] = self.id
                prorate_line = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    self.company_id.id, self.year
                )
                if prorate_line.state not in ("closed", "finale"):
                    raise ValidationError(_("Prorrate year is not closed"))
                precision = self.env["decimal.precision"].precision_get("Account")
                # TODO: bug--> if tax_final_percentage or tax_percentage are 0 --> error. Solve it!
                res["amount"] = round(
                    res["amount"] * (1 - prorate_line.tax_final_percentage / prorate_line.tax_percentage),
                    # res["amount"]-(res["amount"]*(prorate_line.tax_percentage-prorate_line.tax_final_percentage),
                    precision)

            elif map_line.field_number == 43:
                actual_final_prorate = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    self.company_id.id, self.year
                )
                res = {
                    "model": self._name,
                    "res_id": self.id,
                    "map_line_id": map_line.id,
                }
                move_line_ids = []
                amount = 0
                # Validar amb les dades si realment ens podem refiar d'aquest camp.
                # l'altre solució miraria el maxim temps que es pot fer la prorata(10 anys)
                assets_ids = self.env['account.asset'].search(
                    [('capital_asset_type_id', '!=', False),
                     ("state", "=", "open")
                     ])
                # intentar no utilitzar els move_line_id ni els move_line si es possible
                for asset in assets_ids:
                    if all([
                        actual_final_prorate.tax_final_percentage,
                        asset.start_date_use,
                        asset.start_date_use.year == self.year
                    ]):
                        asset.final_prorate_percent = actual_final_prorate.tax_final_percentage
                        # TO_DELETE
                        # asset.final_deductible_VAT_rate = asset.balance * asset.tax_ids.value * asset.final_prorate_percent/100
                        # asset.final_non_deductible_VAT_rate = asset.balance * asset.tax_ids.value * (
                        #     1 - asset.final_prorate_percent/100)
                    if all([
                        asset.start_date_use,
                        asset.start_date_use.year >= self.year - asset.capital_asset_type_id.period,
                        asset.start_date_use.year < self.year
                    ]):
                        percentaje_difference = (asset.final_prorate_percent - actual_final_prorate.tax_final_percentage)
                        if percentaje_difference and percentaje_difference > 1 or percentaje_difference < 1:
                            precision = self.env["decimal.precision"].precision_get("Account")
                            if asset.move_line_id:
                                move_line_ids.append(asset.move_line_id.id)
                            # amount += asset.move_line_id.balance

                            amount += round(
                                asset.tax_base_amount * percentaje_difference/100,
                                precision,
                            )
                res["amount"] = amount
                if move_line_ids:
                    res["move_line_ids"] = [(6, 0, move_line_ids)]

            return res

    @api.model
    def _prepare_counterpart_move_line_prorate(self, account, tax, balance):
        vals = {
            "name": _("Prorate Regularization"),
            "account_id": account.id,
            "tax_line_id": tax,
            "partner_id": self.env.ref("l10n_es_aeat.res_partner_aeat").id,
        }
        precision = self.env["decimal.precision"].precision_get("Account")
        balance = round(balance, precision)
        vals["debit"] = balance if balance > 0 else 0.0
        vals["credit"] = -balance if balance < 0 else 0.0
        return vals

    def create_regularization_move(self):
        super().create_regularization_move()
        if self.period_type in ("4T", "12"):
            self.create_regularization_move_prorate()

    def create_regularization_move_prorate(self):
        self.ensure_one()
        if (
            not self.counterpart_prorate_receivable_account_id
            or not self.counterpart_prorate_payable_account_id
            or not self.journal_id
        ):
            raise UserError(
                _(
                    "You must fill both journal and counterpart receivable/payable account."
                )
            )
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
        lines = self._process_tax_line_regularization_prorate(
            self.tax_line_ids.filtered("to_regularize_prorate")
        )
        lines += self._prepare_regularization_extra_move_lines()
        tax_balances = {}
        for line in lines:
            tax_balances.setdefault(line["tax_line_id"], 0)
            tax_balances[line["tax_line_id"]] += line["debit"] - line["credit"]
        for tax, balance in tax_balances.items():
            account = (
                self.counterpart_prorate_receivable_account_id
                if balance < 0
                else self.counterpart_prorate_payable_account_id
            )
            regularize_line = self._prepare_counterpart_move_line_prorate(
                account, tax, -balance
            )
            lines.append(regularize_line)
        return lines


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    move_prorate_id = fields.Many2one(
        comodel_name="account.move",
        string="Account entry",
        readonly=True,
        domain=[("type", "=", "entry")],
    )

    def button_unpost(self):
        """Remove created account move entry and set state to cancelled."""
        self.mapped("move_prorate_id").with_context(force_delete=True).unlink()
        super().button_unpost()
        return True

    def button_open_move(self):
        action = super().button_open_move()
        move_ids = list(filter(None, [self.move_prorate_id.id, self.move_id.id]))
        action["domain"] = [("id", "in", move_ids)]
        action["view_mode"] = "tree,form"
        del action["res_id"]
        return action
