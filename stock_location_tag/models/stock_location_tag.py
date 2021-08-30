# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockLocationTag(models.Model):
    _name = "stock.location.tag"
    _description = "Location Tags"

    name = fields.Char(required=True, translate=True)
    color = fields.Integer(string="Color Index")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=True,
        required=True,
    )

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name,company_id)",
            "Tag name already exists. It must be unique per company!",
        ),
    ]
