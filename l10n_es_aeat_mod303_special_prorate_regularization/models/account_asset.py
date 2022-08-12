# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

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


class AccountAsset(models.Model):
    _inherit = "account.asset"

    partner_vat = fields.Char(string="VAT", related="partner_id.vat")

    def _compute_vat(self):
        for rec in self:
            rec.partner_vat = rec.partner_id.vat

    start_date_use = fields.Date(string="Accounting Date", related="move_id.date")
    invoice_date = fields.Date(string="Invoice Date", related="move_id.invoice_date")
    amount_currency = fields.Float(
        string="Amount Currency", compute="_compute_amount_currency"
    )

    def _compute_amount_currency(self):
        for rec in self:
            rec.amount_currency = rec.move_line_id.amount_currency

    tax_id = fields.Many2one(string="Tax", compute="_compute_tax_id")

    def _compute_tax_id(self):
        for rec in self:
            # TODO: hacer el filtro en el mapping de la casilla 43
            rec.tax_id = rec.move_line_id.mapped("tax_ids").mapped("name")

    # comprobar si hay != 1, raise.
    # en el tax id asignamos el que nos devuelva

    # TODO: compute store=False /related vs compute store=True vs calcule on asset creation
    temp_prorate_percent = fields.Float(
        string="Temporary prorrate (%)", compute="_compute_tax_percentage"
    )
    final_prorate_percent = fields.Float(
        string="Final prorrate (%)", compute="_compute_tax_percentage"
    )

    def _compute_tax_percentage(self):
        for rec in self:
            percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                rec.company_id.id, rec.start_date_use.year
            )
            rec.temp_prorrate_percent = percentage_line.tax_percentage
            rec.final_prorrate_percent = percentage_line.tax_final_percentage

    # iva_ded_prov = fields.Float(string="IVA Deducible Provisional",
    # compute="_compute_iva_ded_prov")
    #
    # def _compute_iva_ded_prov(self):
    #     for rec in self:
    #         prorate_line = rec.env['aeat.map.special.prorrate.year']
    #         .get_by_ukey(rec.company_id.id, rec.date.year)
    #         rec.amount_currency = rec.move_line_id.amount_currency

    # investment_asset_type=fields.Selection(string="Type of Investment Asset", related=""

    cancellation_date = fields.Date(string="Cancellation date")

    # investment_good_affectacion = fields.Selection(selection=[
    #     ('subject', _("Subject")), ('exempt', _("Exempt")),
    #     ('prorrate', _("Prorrate (temporary)"))])


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    def button_post_capital_assets(self):
        for _report in self:
            pass
            # report.create_regularization_move_prorate()
            # self.write({"state": "posted"})
            # return True
