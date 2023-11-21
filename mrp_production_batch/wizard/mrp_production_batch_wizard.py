# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MRPProductionBatchWizard(models.TransientModel):
    _name = "mrp.production.batch.wizard"
    _description = "MRP Production Batch wizard"

    production_ids = fields.One2many(
        comodel_name="mrp.production.batch.line.wizard",
        inverse_name="production_batch_wizard_id",
    )
    operation_type = fields.Many2one(
        comodel_name="stock.picking.type",
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
    )

    def action_mrp_production_batch_group(self):
        self.ensure_one()
        model = self.env.context.get("active_model")
        mrp_production_ids = self.env[model].browse(self.env.context.get("active_ids"))
        production_batch = self.env["mrp.production.batch"].create(
            {
                "name": self.operation_type.sequence_id._next(),
                "creation_date": fields.Datetime.now(),
                "production_ids": [
                    (6, 0, mrp_production_ids.ids),
                ],
                "operation_type": self.operation_type.id,
            }
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_production_batch.mrp_production_batch_action"
        )
        action["views"] = [
            (
                self.env.ref("mrp_production_batch.mrp_production_batch_form_view").id,
                "form",
            )
        ]
        action["res_id"] = production_batch.id
        return action
