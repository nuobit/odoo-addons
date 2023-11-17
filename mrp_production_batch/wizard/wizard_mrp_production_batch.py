# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MRPProductionBatchWizard(models.TransientModel):
    _name = "mrp.production.batch.wizard"
    _description = "MRP Production Batch wizard"

    manufacturing_ids = fields.One2many(
        comodel_name="mrp.production.batch.line.wizard",
        inverse_name="mrp_production_batch_id",
        readonly=False,
        store=True,
    )

    def action_mrp_production_batch_group(self):
        self.ensure_one()
        res = self.env["mrp.production.batch"].create(
            {
                "production_ids": [
                    (6, 0, self.manufacturing_ids.ids),
                ],
            }
        )
        for production in self.manufacturing_ids:
            production.production_batch_id = res.id
