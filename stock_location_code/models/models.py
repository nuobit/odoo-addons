# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Location(models.Model):
    _inherit = "stock.location"

    code = fields.Char(string="Code")

    _sql_constraints = [
        (
            "location_code_uniq",
            "unique(code, company_id)",
            "A code can only be assigned to one location per company!",
        ),
    ]
