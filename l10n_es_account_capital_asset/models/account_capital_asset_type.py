# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CapitalAssetType(models.Model):
    _name = "l10n.es.account.capital.asset.type"

    name = fields.Char(string="Name", required=True, translate=True)
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

    def name_get(self):
        return [(rec.id, "%s (%i years)" % (rec.name, rec.period)) for rec in self]

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if rec.period <= 0:
                raise ValidationError(_("Period must be greater than 0."))
