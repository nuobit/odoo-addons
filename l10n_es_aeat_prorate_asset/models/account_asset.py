# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.account_asset_management.models.account_asset import READONLY_STATES


class AccountAsset(models.Model):
    _inherit = "account.asset"

    map_special_prorate_year_id = fields.Many2one(
        comodel_name="aeat.map.special.prorrate.year",
        compute="_compute_map_special_prorate_year_id",
    )

    @api.depends("date_start")
    def _compute_map_special_prorate_year_id(self):
        for rec in self:
            if rec.date_start:
                rec.map_special_prorate_year_id = rec.env[
                    "aeat.map.special.prorrate.year"
                ].get_by_ukey(rec.company_id.id, rec.date_start.year)
            else:
                rec.map_special_prorate_year_id = False

    def _compute_prorate_amounts(self, percent, is_deductible=True):
        self.ensure_one()
        ratio = percent / 100
        if not is_deductible:
            ratio = 1 - ratio
        return self.vat_tax_amount * ratio

    temp_deductible_tax_amount = fields.Float(
        string="Temporal Deductible VAT Amount",
        compute="_compute_temp_deductible_tax_amount",
        store=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "temp_prorate_percent")
    def _compute_temp_deductible_tax_amount(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                rec.temp_deductible_tax_amount = rec._compute_prorate_amounts(
                    rec.map_special_prorate_year_id.tax_percentage
                )

    temp_non_deductible_tax_amount = fields.Float(
        string="Temporal Non-Deductible VAT Amount",
        compute="_compute_temp_non_deductible_tax_amount",
        store=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "temp_prorate_percent")
    def _compute_temp_non_deductible_tax_amount(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                rec.temp_non_deductible_tax_amount = rec._compute_prorate_amounts(
                    rec.map_special_prorate_year_id.tax_percentage, is_deductible=False
                )

    final_deductible_tax_amount = fields.Float(
        string="Final Deductible VAT Amount",
        compute="_compute_final_deductible_tax_amount",
        store=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "final_prorate_percent")
    def _compute_final_deductible_tax_amount(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                rec.final_deductible_tax_amount = rec._compute_prorate_amounts(
                    rec.map_special_prorate_year_id.tax_final_percentage
                )

    final_non_deductible_tax_amount = fields.Float(
        string="Final Non-Deductible VAT Amount",
        compute="_compute_final_non_deductible_tax_amount",
        store=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "final_prorate_percent")
    def _compute_final_non_deductible_tax_amount(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                rec.final_non_deductible_tax_amount = rec._compute_prorate_amounts(
                    rec.map_special_prorate_year_id.tax_final_percentage,
                    is_deductible=False,
                )

    temp_prorate_percent = fields.Float(
        string="Temporary prorate (%)",
        compute="_compute_temp_prorate_percent",
        store=True,
        readonly=False,
        states=READONLY_STATES,
    )

    @api.depends("map_special_prorate_year_id.tax_percentage")
    def _compute_temp_prorate_percent(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                if (
                    rec.temp_prorate_percent
                    != rec.map_special_prorate_year_id.tax_percentage
                ):
                    rec.temp_prorate_percent = (
                        rec.map_special_prorate_year_id.tax_percentage
                    )

    final_prorate_percent = fields.Float(
        string="Final Prorate (%)",
        compute="_compute_final_prorate_percent",
        store=True,
        readonly=False,
        states=READONLY_STATES,
    )

    @api.depends("map_special_prorate_year_id.tax_final_percentage")
    def _compute_final_prorate_percent(self):
        for rec in self:
            if rec.map_special_prorate_year_id:
                if (
                    rec.final_prorate_percent
                    != rec.map_special_prorate_year_id.tax_final_percentage
                ):
                    rec.final_prorate_percent = (
                        rec.map_special_prorate_year_id.tax_final_percentage
                    )

    prorate_tax_id = fields.Many2one(
        string="Prorate Tax",
        comodel_name="account.tax",
        compute="_compute_prorate_tax_id",
        store=True,
    )

    @api.depends("vat_tax_id", "vat_tax_id.prorate")
    def _compute_prorate_tax_id(self):
        for rec in self:
            taxes = rec.vat_tax_id.filtered(lambda x: x.prorate)
            if len(taxes) > 1:
                raise ValidationError(
                    _("Asset has more than 1 Prorate tax. Please, review the taxes")
                )
            rec.prorate_tax_id = taxes._origin

    @api.constrains(
        "temp_prorate_percent",
        "final_prorate_percent",
    )
    def _check_move_line(self):
        for rec in self:
            if rec.date_start:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.date_start.year
                )
                if percentage_line and (
                    percentage_line.tax_final_percentage != rec.final_prorate_percent
                    or percentage_line.tax_percentage != rec.temp_prorate_percent
                ):
                    raise ValidationError(
                        _(
                            "It's not possible to modify the temporary or final prorate "
                            "if already exists value in this years. Temp: %s, Final: %s"
                            % (
                                percentage_line.tax_percentage,
                                percentage_line.tax_final_percentage,
                            )
                        )
                    )
