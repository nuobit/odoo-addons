# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    temp_deductible_tax_amount = fields.Monetary(
        string="Temporal Deductible VAT Amount",
        compute="_compute_temp_deductible_tax_amount",
        store=True,
        readonly=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "temp_prorate_percent")
    def _compute_temp_deductible_tax_amount(self):
        for rec in self:
            if all([rec.prorate_tax_id, rec.temp_prorate_percent, rec.tax_base_amount]):
                rec.temp_deductible_tax_amount = (
                    rec.tax_total_amount * rec.temp_prorate_percent / 100
                )
            else:
                rec.temp_deductible_tax_amount = 0

    temp_non_deductible_tax_amount = fields.Monetary(
        string="Temporal Non-Deductible VAT Amount",
        compute="_compute_temp_non_deductible_tax_amount",
        store=True,
        readonly=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "temp_prorate_percent")
    def _compute_temp_non_deductible_tax_amount(self):
        for rec in self:
            if all([rec.prorate_tax_id, rec.temp_prorate_percent, rec.tax_base_amount]):
                rec.temp_non_deductible_tax_amount = rec.tax_total_amount * (
                    1 - rec.temp_prorate_percent / 100
                )
            else:
                rec.temp_non_deductible_tax_amount = 0

    final_deductible_tax_amount = fields.Monetary(
        string="Final Deductible VAT Amount",
        compute="_compute_final_deductible_tax_amount",
        store=True,
        readonly=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "final_prorate_percent")
    def _compute_final_deductible_tax_amount(self):
        for rec in self:
            if all(
                [rec.prorate_tax_id, rec.final_prorate_percent, rec.tax_base_amount]
            ):
                rec.final_deductible_tax_amount = (
                    rec.tax_total_amount * rec.final_prorate_percent / 100
                )
            else:
                rec.final_deductible_tax_amount = 0

    final_non_deductible_tax_amount = fields.Monetary(
        string="Final Non-Deductible VAT Amount",
        compute="_compute_final_non_deductible_tax_amount",
        store=True,
        readonly=True,
    )

    @api.depends("prorate_tax_id", "tax_base_amount", "final_prorate_percent")
    def _compute_final_non_deductible_tax_amount(self):
        for rec in self:
            if all(
                [rec.prorate_tax_id, rec.final_prorate_percent, rec.tax_base_amount]
            ):
                rec.final_non_deductible_tax_amount = rec.tax_total_amount * (
                    1 - rec.final_prorate_percent / 100
                )
            else:
                rec.final_non_deductible_tax_amount = 0

    temp_prorate_percent = fields.Float(
        string="Temporary prorate (%)",
        compute="_compute_temp_prorate_percent",
        store=True,
        readonly=False,
    )

    @api.depends("date_start")
    def _compute_temp_prorate_percent(self):
        for rec in self:
            if rec.date_start:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.date_start.year
                )
                rec.temp_prorate_percent = percentage_line.tax_percentage
            else:
                rec.temp_prorate_percent = False

    final_prorate_percent = fields.Float(
        string="Final Prorate (%)",
        compute="_compute_final_prorate_percent",
        store=True,
        readonly=False,
    )

    @api.depends("date_start")
    def _compute_final_prorate_percent(self):
        for rec in self:
            if rec.date_start:
                percentage_line = rec.env["aeat.map.special.prorrate.year"].get_by_ukey(
                    rec.company_id.id, rec.date_start.year
                )
                rec.final_prorate_percent = percentage_line.tax_final_percentage
            else:
                rec.final_prorate_percent = False

    prorate_tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
        store=True,
        domain="[('prorate', '=', True)]",
        compute="_compute_prorate_tax_id",
    )

    @api.depends("tax_ids")
    def _compute_prorate_tax_id(self):
        for rec in self:
            taxes = rec.tax_ids.filtered(lambda x: x.prorate is True)
            if len(taxes) > 1:
                raise ValidationError(
                    _("Asset has more than 1 Prorate tax." " Please, review the taxes")
                )
            rec.prorate_tax_id = taxes

    tax_total_amount = fields.Monetary(
        string="Tax Total Amount",
        compute="_compute_tax_total_amount",
    )

    def _compute_tax_total_amount(self):
        for rec in self:
            rec.tax_total_amount = rec.tax_base_amount * rec.prorate_tax_id.amount / 100

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
