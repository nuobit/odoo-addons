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
        string="Number of Manufacturing Orders to Process without Batch",
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

    count_pb_todo = fields.Integer(compute="_compute_count_pb")
    count_pb_waiting = fields.Integer(compute="_compute_count_pb")

    def _compute_count_pb(self):
        mrp_picking_types = self.filtered(
            lambda picking: picking.code == "mrp_operation_batch"
        )
        if not mrp_picking_types:
            self.count_pb_waiting = False
            self.count_pb_todo = False
            return
        domains = {
            "count_pb_waiting": [("state", "=", "in_progress")],
            "count_pb_todo": [("state", "!=", "done")],
        }
        for field in domains:
            data = self.env["mrp.production.batch"].read_group(
                domains[field] + [("operation_type", "in", self.ids)],
                ["operation_type"],
                ["operation_type"],
            )
            count = {x["operation_type"][0]: x["operation_type_count"] for x in data}
            for picking in mrp_picking_types:
                picking[field] = count.get(picking.id, 0)
        remaining = self - mrp_picking_types
        if remaining:
            remaining.count_pb_waiting = False
            remaining.count_pb_todo = False

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

    def get_mrp_production_batch_stock_picking_action_picking_type(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_production_batch.mrp_production_batch_action_picking_dashboard"
        )
        action["display_name"] = self.display_name
        return action
