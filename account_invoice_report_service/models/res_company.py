# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_service_id = fields.Many2one(
        string="Service Invoice report",
        comodel_name="ir.actions.report",
        domain=[
            ("model", "=", "account.invoice"),
        ],
    )
