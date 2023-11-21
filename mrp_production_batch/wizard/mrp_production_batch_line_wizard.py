# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MRPProductionBatchLineWizard(models.TransientModel):
    _name = "mrp.production.batch.line.wizard"
    _description = "MRP Production Line Batch wizard"

    production_batch_wizard_id = fields.Many2one(
        comodel_name="mrp.production.batch.wizard",
        required=True,
        ondelete="cascade",
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )
