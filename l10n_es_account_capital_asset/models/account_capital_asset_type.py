# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CapitalAssetType(models.Model):
    _name = "l10n.es.account.capital.asset.type"
    _description = "Capital Asset Type"

    name = fields.Char(required=True, translate=True)
    period = fields.Integer(string="Period (years)", required=True)

    _sql_constraints = [
        (
            "unique_name",
            "unique(name)",
            "Capital Asset Type name must be unique",
        ),
        (
            "unique_period",
            "unique(period)",
            "Capital Asset Type period must be unique",
        ),
    ]

    @api.depends("name", "period")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} ({rec.period} {_('years')})"

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if rec.period <= 0:
                raise ValidationError(_("Period must be greater than 0."))

    @api.model
    def _get_max_period(self):
        return max(self.search([]).mapped("period"))
