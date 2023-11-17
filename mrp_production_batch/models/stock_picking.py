# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    mo_todo_wo_batch_count = fields.Integer(
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
                rec.mo_todo_wo_batch_count = count.get(rec.id, 0)
            else:
                rec.mo_todo_wo_batch_count = False

    mo_batch_count = fields.Integer(
        compute="_compute_mo_batch_count",
    )

    def _get_production_batch_ids(self):
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
        return (
            self.env["mrp.production"]
            .search(
                domains["count_mo_todo"]
                + [
                    ("state", "not in", ("done", "cancel")),
                    ("picking_type_id", "in", self.ids),
                    ("production_batch_id", "!=", False),
                ],
            )
            .mapped("production_batch_id")
        )

    def _compute_mo_batch_count(self):
        for rec in self:
            rec.mo_batch_count = len(self._get_production_batch_ids()) or False
