# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    sequence_production_batch_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Production Batch Sequence",
    )
