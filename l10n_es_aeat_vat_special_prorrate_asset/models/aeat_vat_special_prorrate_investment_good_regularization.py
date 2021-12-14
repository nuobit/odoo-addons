# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AEATVatspecialProrrateInvestmentRegularization(models.Model):
    _name = "aeat.vat.special.prorrate.investment.good.regularization"

    name = fields.Char(string="Name")

    year = fields.Integer(string="Year", required=True)

    amount = fields.Float(string="Amount", required=True)

    investment_good_id = fields.Many2one(comodel_name="account.asset.asset")
