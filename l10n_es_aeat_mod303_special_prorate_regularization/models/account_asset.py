# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        bi_tax_templates = self.env['l10n.es.aeat.map.tax'].search([('model', '=', 303)]).filtered(
            lambda x: x.date_to == False).map_line_ids.filtered(lambda x: x.field_number == 43).tax_ids
        bi_taxes = self.company_id.get_taxes_from_templates(bi_tax_templates)
        taxes = aml.tax_ids.filtered(lambda x: x in bi_taxes)
        if not taxes:
            return vals

        # TODO: mirar si es legitim que NO hi hagi mes d'una tax
        if len(taxes) > 1:
            raise ValidationError(
                _("Asset has more than 1 Capital Asset Prorate tax. Please, review the invoice %s") % self.display_name)

        # TODO: veure on posar els >= 3005.06€ per a no posar-los harcoded. ¿¿rec_config_settings??
        if aml.balance >= 3005.06:
            vals["capital_asset_type_id"] = aml.asset_profile_id.capital_asset_type_id

        prorate_year = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
            self.company_id.id, self.date.year
        )
        if not prorate_year:
            raise ValidationError(
                _("Prorate not found in company %s in the year %s") % (self.company_id.display_name, self.year)
            )

        vals.update(
            {
                "purchase_value": aml._get_asset_base_value(),
                "partner_vat": self.partner_id.vat,
                "invoice_number": self.name,
                "start_date_use": self.date,
                "invoice_date": self.invoice_date,
                "tax_base_amount": aml.balance,
                "tax_ids": taxes,
                "temp_prorate_percent": prorate_year.tax_percentage,
            }
        )
        return vals


class AccountAsset(models.Model):
    _inherit = "account.asset"

    partner_vat = fields.Char(string="VAT")
    invoice_number = fields.Char(string="Invoice Number")
    start_date_use = fields.Date(string="Accounting Date")
    invoice_date = fields.Date(string="Invoice Date")
    tax_base_amount = fields.Monetary(string="Tax Base Amount")
    tax_total_amount = fields.Monetary(string="Tax Total Amount", compute="_compute_tax_total_amount", store=False, readonly=True)
    def _compute_tax_total_amount(self):
        for rec in self:


    provisional_deductible_VAT_rate = fields.Monetary(string="Provisional Deductible VAT Rate",
                                                      compute="_compute_provisional_deductible_VAT_rate", store=True,
                                                      readonly=False)

    @api.depends('tax_ids', 'tax_base_amount', 'temp_prorate_percent')
    def _compute_provisional_deductible_VAT_rate(self):
        for rec in self:
            if all([rec.tax_ids, rec.temp_prorate_percent, rec.tax_base_amount]):
                rec.provisional_deductible_VAT_rate = rec.tax_base_amount * rec.tax_ids.amount / 100 * rec.temp_prorate_percent / 100
            else:
                rec.provisional_deductible_VAT_rate = 0

    provisional_non_deductible_VAT_rate = fields.Monetary(string="Provisional Non-Deductible VAT Rate",
                                                          compute="_compute_provisional_non_deductible_VAT_rate",
                                                          store=True,
                                                          readonly=False)

    @api.depends('tax_ids', 'tax_base_amount', 'temp_prorate_percent')
    def _compute_provisional_non_deductible_VAT_rate(self):
        for rec in self:
            if all([rec.tax_ids, rec.temp_prorate_percent, rec.tax_base_amount]):
                rec.provisional_non_deductible_VAT_rate = rec.tax_base_amount * rec.tax_ids.amount / 100 * (
                    1 - rec.temp_prorate_percent / 100)
            else:
                rec.provisional_non_deductible_VAT_rate = 0

    final_deductible_VAT_rate = fields.Monetary(string="Final Deductible VAT Rate",
                                                compute="_compute_final_deductible_VAT_rate", store=True,
                                                readonly=False)

    @api.depends('tax_ids', 'tax_base_amount', 'final_prorate_percent')
    def _compute_final_deductible_VAT_rate(self):
        for rec in self:
            if all([rec.tax_ids, rec.final_prorate_percent, rec.tax_base_amount]):
                rec.final_deductible_VAT_rate = rec.tax_base_amount * rec.tax_ids.amount / 100 * rec.final_prorate_percent / 100
            else:
                rec.final_deductible_VAT_rate = 0

    final_non_deductible_VAT_rate = fields.Monetary(string="Final Non-Deductible VAT Rate",
                                                    compute="_compute_final_non_deductible_VAT_rate", store=True,
                                                    readonly=False)

    @api.depends('tax_ids', 'tax_base_amount', 'final_prorate_percent')
    def _compute_final_non_deductible_VAT_rate(self):
        for rec in self:
            if all([rec.tax_ids, rec.final_prorate_percent, rec.tax_base_amount]):
                rec.final_non_deductible_VAT_rate = rec.tax_base_amount * rec.tax_ids.amount / 100 * (
                    1 - rec.final_prorate_percent / 100)
            else:
                rec.final_non_deductible_VAT_rate = 0

    currency_id = fields.Many2one(comodel_name='res.currency', related="move_line_id.currency_id", string='Currency')
    capital_asset_type_id = fields.Many2one(string="Capital Asset Type",
                                            comodel_name="aeat.vat.special.prorrate.capital.asset.type")

    # TODO: rename tax_ids name?
    # tax_ids = fields.Many2many(string="Tax", comodel_name="account.tax", column1="asset_id", column2="tax_id",
    #                            store=True)
    # # TODO: domain del tax_ids
    # def _get_taxes_field_43(self):
    #     bi_tax_templates = self.env['l10n.es.aeat.map.tax'].search([('model', '=', 303)]).filtered(
    #         lambda x: x.date_to == False).map_line_ids.filtered(lambda x: x.field_number == 43).tax_ids
    #     bi_taxes = self.company_id.get_taxes_from_templates(bi_tax_templates)
    #     return [('id', 'in', bi_tax_templates.ids)]

    tax_ids = fields.Many2one(string="Tax", comodel_name="account.tax", store=True,
                              domain="[('id', 'in', allowed_tax_ids)]")
    allowed_tax_ids = fields.Many2many(string="Allowed Taxes", comodel_name="account.tax",
                                       compute='_compute_allowed_tax_ids')

    def _compute_allowed_tax_ids(self):
        # TODO: Code used multiple times. Put it on aeat.map.tax as api model
        field_43_taxes = self.env['l10n.es.aeat.map.tax'].search([('model', '=', 303)]).filtered(
            lambda x: x.date_to == False).map_line_ids.filtered(lambda x: x.field_number == 43).tax_ids
        for rec in self:
            rec.allowed_tax_ids = rec.company_id.get_taxes_from_templates(field_43_taxes)

    # TODO: compute store=False /related vs compute store=True vs calcule on asset creation
    temp_prorate_percent = fields.Float(
        string="Temporary prorate (%)", compute="_compute_temp_prorate_percent", store=True, readonly=False
    )

    @api.depends('start_date_use')
    def _compute_temp_prorate_percent(self):
        for rec in self:
            if rec.start_date_use:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.start_date_use.year
                )
                rec.temp_prorate_percent = percentage_line.tax_percentage
            else:
                rec.temp_prorate_percent = False

    final_prorate_percent = fields.Float(
        string="Final prorate (%)", compute="_compute_final_prorate_percent", store=True, readonly=False
    )

    @api.depends('start_date_use')
    def _compute_final_prorate_percent(self):
        for rec in self:
            if rec.start_date_use:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.start_date_use.year
                )
                rec.final_prorate_percent = percentage_line.tax_final_percentage
            else:
                rec.final_prorate_percent = False

    @api.constrains("partner_vat", "invoice_date", "start_date_use", "tax_base_amount",
                    # TODO: in the future probably we will need this tax_id restrict, but now we need to modify tax_ids
                    # "tax_ids",
                    "temp_prorate_percent", "final_prorate_percent", "invoice_number")
    def _check_move_line(self):
        for rec in self:
            if rec.move_line_id:
                if any([
                    rec.invoice_number != rec.move_line_id.move_id.name,
                    rec.start_date_use != rec.move_id.date,
                    rec.invoice_date != rec.move_id.invoice_date,
                    rec.tax_base_amount != rec.move_line_id.amount_currency
                ]):
                    raise ValidationError(
                        _("It's not possible to modify the capital assets fields if asset has move line"))
            if rec.start_date_use:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.start_date_use.year
                )
                if percentage_line and percentage_line.tax_final_percentage != rec.final_prorate_percent or percentage_line.tax_percentage != rec.temp_prorate_percent:
                    raise ValidationError(
                        _("It's not possible to modify the temporary or final prorate if already exists value in this years"))

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

# class L10nEsAeatReport(models.AbstractModel):
#     _inherit = "l10n.es.aeat.report"
#
#     move_capital_asset_id=fields.Many2one(
#         comodel_name="account.move",
#         string="Account entry",
#         readonly=True,
#         domain=[("type", "=", "entry")],
#     )

# def button_post_capital_assets(self):
#     for _report in self:
#         pass
#         # report.create_regularization_move_prorate()
#         # self.write({"state": "posted"})
#         # return True
