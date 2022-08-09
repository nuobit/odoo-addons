# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError


class FirstRegularizationB(models.Model):
    _inherit = "l10n.es.aeat.map.tax.line"

    to_regularize_prorate = fields.Boolean(default=False, string="To Regularize Prorata")


class L10nEsAeatTaxLine(models.Model):
    _inherit = "l10n.es.aeat.tax.line"

    to_regularize_prorate = fields.Boolean(related="map_line_id.to_regularize_prorate", readonly=True)


# to_regularize_equity_ = fields.Boolean(default=False, string="To Regularize Equity")

class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    casilla_44 = fields.Float(
        string=u"[44] Regularización de la prorrata", default=0,
        states={'done': [('readonly', True)]},
        help=u"Regularización por aplicación del porcentaje definitivo de "
             u"prorrata.")

    def _default_counterpart_prorate_receivable_account_id(self):
        return self.get_account_from_template(self.env.ref('l10n_es.account_common_6341'))

    counterpart_prorate_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Counterpart Prorate Account Receivable",
        default=_default_counterpart_prorate_receivable_account_id,
        domain="[('company_id', '=', company_id)]",
    )

    def _default_counterpart_prorate_payable_account_id(self):
        return self.get_account_from_template(self.env.ref('l10n_es.account_common_6391'))

    counterpart_prorate_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        default=_default_counterpart_prorate_payable_account_id,
        string="Counterpart Prorate Payable Account",
        domain="[('company_id', '=', company_id)]",
    )

    # @api.depends("total_devengado", "total_deducir")
    # def _compute_casilla_44(self):
    #     for report in self:
    #         report.casilla_44 = 9999
    # def _get_move_line_domain(self, date_start, date_end, map_line):
    #     domain = super(L10nEsAeatMod303Report, self)._get_move_line_domain(date_start, date_end, map_line)
    #     if map_line.field_number != 44:
    #         domain.append(('tax_repartition_line_id.account_id', '!=', False))
    #     return domain

    def _process_tax_line_regularization_prorate(self, tax_lines):
        self.ensure_one()
        groups = self.env["account.move.line"].read_group(
            [
                ("id", "in", tax_lines.move_line_ids.ids),
                ("parent_state", "=", "posted"),
            ],
            ["account_id", "tax_line_id", "balance", "debit", "credit"],
            ["account_id", "tax_line_id"],
            lazy=False
        )
        lines = []
        prorate_line = self.env['aeat.map.special.prorrate.year'].get_by_ukey(self.company_id.id, self.year)
        if prorate_line.state not in ('closed', 'finale'):
            raise ValidationError(_("Prorrate year is not closed"))
        for group in groups:
            balance = group['balance'] * round((prorate_line.tax_final_percentage - prorate_line.tax_percentage) / 100,
                                               2)
            if balance:
                group["debit"] = balance if balance > 0 else 0
                group["credit"] = -balance if balance < 0 else 0
                lines.append(self._prepare_regularization_move_line(group))
        return lines

    @api.model
    def _prepare_regularization_move_line_prorate(self, account_group):
        return {
            **self._prepare_regularization_move_line(account_group),
            "tax_line_id": account_group['tax_line_id'][0],
        }

    def _prepare_tax_line_vals(self, map_line):
        if map_line.field_number != 44:
            return super(L10nEsAeatMod303Report, self)._prepare_tax_line_vals(map_line)
        self.ensure_one()
        if self.period_type in ("4T", "12"):
            date_start = "%s-01-01" % self.year
            date_end = "%s-12-31" % self.year
            move_lines = self._get_tax_lines(date_start, date_end, map_line)
            # to_delete
            # move_lines = move_lines.filtered(lambda x: x.tax_repartition_line_id.account_id == x.account_id)
            prorate_line = self.env['aeat.map.special.prorrate.year'].get_by_ukey(self.company_id.id, self.year)
            if prorate_line.state not in ('closed', 'finale'):
                raise ValidationError(_("Prorrate year is not closed"))
            # amount = round(
            #     sum(move_lines.mapped("balance")) * prorate_line.tax_final_percentage / prorate_line.tax_percentage, 2)
            balance = sum(move_lines.mapped("balance"))
            amount = balance * round((prorate_line.tax_final_percentage - prorate_line.tax_percentage) / 100, 2)
            return {
                "model": self._name,
                "res_id": self.id,
                "map_line_id": map_line.id,
                "amount": amount,
                "move_line_ids": [(6, 0, move_lines.ids)],
            }

    def create_regularization_move_prorate(self):
        self.ensure_one()
        if not self.counterpart_prorate_receivable_account_id or not self.counterpart_prorate_payable_account_id or not self.journal_id:
            raise exceptions.UserError(
                _("You must fill both journal and counterpart receivable/payable account.")
            )
        move_vals = self._prepare_move_vals()
        line_vals_list = self._prepare_regularization_move_lines_prorate()
        move_vals["line_ids"] = [(0, 0, x) for x in line_vals_list]
        self.move_id = self.env["account.move"].create(move_vals)

    def _prepare_regularization_move_lines_prorate(self):
        self.ensure_one()
        lines = self._process_tax_line_regularization_prorate(
            self.tax_line_ids.filtered("to_regularize_prorate")
        )
        lines += self._prepare_regularization_extra_move_lines()
        # Write counterpart with the remaining
        debit = sum(x["debit"] for x in lines)
        credit = sum(x["credit"] for x in lines)
        regularize_line = self._prepare_counterpart_move_line(
            self.counterpart_prorate_receivable_account_id, debit, credit
        )
        if regularize_line["debit"] != 0:
            regularize_line["account_id"] = self.counterpart_prorate_payable_account_id.id
        lines.append(regularize_line)
        return lines


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    def button_post_prorate(self):
        for report in self:
            report.create_regularization_move_prorate()
            # self.write({"state": "posted"})
            return True
