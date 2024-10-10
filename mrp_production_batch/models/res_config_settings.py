# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sequence_production_batch_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Production Batch Sequence",
        related="company_id.sequence_production_batch_id",
        readonly=False,
    )
