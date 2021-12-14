# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AEATVatspecialProrrateInvestmentType(models.Model):
    _name = "aeat.vat.special.prorrate.investment.good.type"

    name = fields.Char(string="Name", required=True, translate=True)

    period = fields.Integer(string="Period (years)", required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id.id,
    )

    _sql_constraints = [
        (
            "unique_name",
            "unique(name, company_id)",
            "Investment good name must be unique",
        ),
    ]

    @api.multi
    def name_get(self):
        return [(rec.id, "%s (%i years)" % (rec.name, rec.period)) for rec in self]

    @api.constrains("period")
    def check_period(self):
        for rec in self:
            if rec.period <= 0:
                raise ValidationError(_("Period must be greater than 0."))
