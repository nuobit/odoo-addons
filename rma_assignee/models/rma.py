# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Rma(models.Model):
    _inherit = "rma"

    user_assignee_id = fields.Many2one(
        string="Assigned To",
        comodel_name="res.users",
        ondelete="restrict",
        domain="['|',('company_id', '=', False), ('company_id', '=', company_id)]",
    )
