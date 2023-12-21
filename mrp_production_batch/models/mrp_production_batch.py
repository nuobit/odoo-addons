# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


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

    total_production_count = fields.Integer(
        compute="_compute_total_production_count",
    )

    def _compute_total_production_count(self):
        for rec in self:
            rec.total_production_count = len(rec.production_ids)

    to_review_production_count = fields.Integer(
        compute="_compute_production_wo_batch_count",
    )
    ready_production_count = fields.Integer(
        compute="_compute_production_wo_batch_count",
    )

    def _compute_production_wo_batch_count(self):
        for rec in self:
            rec.ready_production_count = len(
                rec.production_ids.filtered(lambda r: r.is_ready_to_produce)
            )
            rec.to_review_production_count = len(
                rec.production_ids.filtered(lambda r: not r.is_ready_to_produce)
            )

    cancelled_production_count = fields.Integer(
        compute="_compute_cancelled_production_count",
    )

    def _compute_cancelled_production_count(self):
        for rec in self:
            rec.cancelled_production_count = len(
                rec.production_ids.filtered(lambda r: r.state == "cancel")
            )

    creation_date = fields.Date(
        string="Creation Date",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        default="draft",
        compute="_compute_state",
        store=True,
    )

    @api.depends("production_ids.state", "production_wo_lot_producing_id")
    def _compute_state(self):
        for rec in self:
            if not rec.production_wo_lot_producing_id:
                if rec.production_ids.filtered(
                    lambda r: r.state not in ["done", "cancel"]
                ):
                    rec.state = "in_progress"
                else:
                    rec.state = "done"
            else:
                rec.state = "draft"

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
            rec.product_ids = rec.production_ids.product_id

    def action_done(self):
        self.ensure_one()
        productions = self.production_ids.filtered(lambda r: r.state != "cancel")
        for production in productions:
            production.with_context(mrp_production_batch_create=True).button_mark_done()

    def action_check(self):
        self.ensure_one()
        productions = self.production_ids.filtered(lambda r: not r.is_ready_to_produce)
        len_production = len(productions)
        productions_not_ready = []
        for production in productions:
            raise_msg = _("Is Ready To Produce")
            try:
                with self.env.cr.savepoint():
                    production.with_context(
                        mrp_production_batch_create=True
                    ).button_mark_done()
                    raise ValidationError(raise_msg)
            except (ValidationError, UserError) as e:
                production.is_ready_to_produce = bool(e.name == raise_msg)
                if not production.is_ready_to_produce:
                    productions_not_ready.append(production.display_name)
                    production.error_message = e.name
                else:
                    production.error_message = False
        if not self.env.context.get("mrp_production_check"):
            if productions_not_ready and len(productions_not_ready) == len_production:
                message = "The following productions could not be marked as 'done':\n"
                message += "\n".join(productions_not_ready)
                raise UserError(message)

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

    def action_view_total_production(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [("id", "in", self.production_ids.ids)]
        return action

    def action_view_production_to_review(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [("id", "in", self.to_review_production_ids.ids)]
        return action

    ready_production_ids = fields.Many2many(
        comodel_name="mrp.production",
        compute="_compute_production_ready_ids",
    )

    def _compute_production_ready_ids(self):
        for rec in self:
            rec.ready_production_ids = rec.production_ids.filtered(
                lambda x: x.is_ready_to_produce
            )

    to_review_production_ids = fields.Many2many(
        comodel_name="mrp.production",
        compute="_compute_production_to_review_ids",
    )

    def _compute_production_to_review_ids(self):
        for rec in self:
            rec.to_review_production_ids = rec.production_ids.filtered(
                lambda x: not x.is_ready_to_produce
            )

    def action_view_production_ready(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [("id", "in", self.ready_production_ids.ids)]
        return action

    def action_view_production_cancelled(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [
            ("id", "in", self.production_ids.ids),
            ("state", "=", "cancel"),
        ]
        return action

    def action_generate_serial(self):
        for rec in self:
            for production in rec.production_wo_lot_producing_id:
                production.action_generate_serial()
