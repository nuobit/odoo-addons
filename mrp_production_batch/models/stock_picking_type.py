# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    code = fields.Selection(
        selection_add=[("mrp_operation_batch", "Manufacturing Batch")],
        ondelete={"mrp_operation_batch": "cascade"},
    )

    count_mo_todo_wo_batch = fields.Integer(
        string="Number of Manufacturing Orders to Process",
        compute="_compute_mo_count",
    )

    def _compute_mo_count(self):
        super()._get_mo_count()
        for rec in self:
            if rec.count_mo_todo:
                domains = {
                    "count_mo_waiting": [("reservation_state", "=", "waiting")],
                    "count_mo_todo": [
                        ("state", "in", ("confirmed", "draft", "progress", "to_close"))
                    ],
                    "count_mo_late": [
                        ("date_planned_start", "<", fields.Date.today()),
                        ("state", "=", "confirmed"),
                    ],
                }
                data = self.env["mrp.production"].read_group(
                    domains["count_mo_todo"]
                    + [
                        ("state", "not in", ("done", "cancel")),
                        ("picking_type_id", "in", self.ids),
                        ("production_batch_id", "=", False),
                    ],
                    ["picking_type_id"],
                    ["picking_type_id"],
                )
                count = {
                    x["picking_type_id"]
                    and x["picking_type_id"][0]: x["picking_type_id_count"]
                    for x in data
                }
                rec.count_mo_todo_wo_batch = count.get(rec.id, 0)
            else:
                rec.count_mo_todo_wo_batch = False

    mo_batches = fields.One2many(
        comodel_name="mrp.production.batch",
        inverse_name="operation_type",
    )
    mo_batch_count = fields.Integer(
        compute="_compute_mo_batch_count",
    )

    def _compute_mo_batch_count(self):
        for rec in self:
            rec.mo_batch_count = len(rec.mo_batches) or False

    def mrp_production_batch_action(self):
        tree_view = self.env.ref("mrp_production_batch.mrp_production_batch_tree_view")
        form_view = self.env.ref("mrp_production_batch.mrp_production_batch_form_view")
        return {
            "name": ("Detailed Operations"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "mrp.production.batch",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "view_id": tree_view.id,
            "domain": [("id", "in", self.mo_batches.ids)],
        }
