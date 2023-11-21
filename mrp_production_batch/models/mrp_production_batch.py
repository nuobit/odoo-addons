# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models


class MrpProductionBatch(models.Model):
    _name = "mrp.production.batch"

    name = fields.Char(
        readonly=True,
        required=True,
    )
    production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="production_batch_id",
        string="Manufacturing Orders",
    )
    production_wo_lot_producing_id = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="production_batch_id",
        compute="_compute_production_wo_lot_producing_id",
    )

    @api.depends("production_ids.lot_producing_id")
    def _compute_production_wo_lot_producing_id(self):
        for rec in self:
            rec.production_wo_lot_producing_id = rec.production_ids.filtered(
                lambda x: not x.lot_producing_id
            )

    production_count = fields.Integer(
        compute="_compute_production_count",
    )

    def _compute_production_count(self):
        for rec in self:
            rec.production_count = len(rec.production_ids)

    pending_production_count = fields.Integer(
        compute="_compute_pending_production_count",
    )

    def _compute_pending_production_count(self):
        for rec in self:
            rec.pending_production_count = len(
                rec.production_ids.filtered(lambda r: r.state != "done")
            )

    creation_date = fields.Date(
        string="Creation Date",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        default="draft",
    )
    operation_type = fields.Many2one(
        comodel_name="stock.picking.type",
        required=True,
        readonly=True,
    )
    product_qty = fields.Float(
        compute="_compute_product_qty",
    )

    @api.depends("production_ids")
    def _compute_product_qty(self):
        for rec in self:
            rec.product_qty = sum(rec.production_ids.mapped("product_qty"))

    product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_product_ids",
        string="Products",
    )

    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = rec.production_ids.mapped("product_id")

    def action_done(self):
        self.ensure_one()
        self.production_ids.with_context(
            mrp_production_batch_create=True
        ).button_mark_done()
        self.state = "done"

    def _get_common_action_view_production(self):
        tree_view = self.env.ref("mrp.mrp_production_tree_view")
        form_view = self.env.ref("mrp.mrp_production_form_view")
        return {
            "name": _("Detailed Operations"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "mrp.production",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "view_id": tree_view.id,
        }

    def action_view_production(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [("id", "in", self.production_ids.ids)]
        return action

    def action_view_production_pending(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [
            ("id", "in", self.production_ids.ids),
            ("state", "!=", "done"),
        ]
        return action

    def action_generate_serial(self):
        for rec in self:
            for production in rec.production_wo_lot_producing_id:
                production.action_generate_serial()
