# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpProductionBatch(models.Model):
    _name = "mrp.production.batch"
    _description = "MRP Production Batch"

    name = fields.Char(compute="_compute_name", store=True)

    @api.depends("state")
    def _compute_name(self):
        for rec in self:
            if rec.name == "/" and rec.state != "draft":
                rec.name = rec.operation_type.sequence_id._next()
            if not rec.name:
                rec.name = "/"

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        index=True,
        required=True,
    )

    production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="production_batch_id",
        string="Manufacturing Orders",
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

    # TODO: Rename to date
    creation_date = fields.Date(
        string="Creation Date",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_state",
        store=True,
    )

    @api.depends("production_ids.is_ready_to_produce", "production_ids.state")
    def _compute_state(self):
        for rec in self:
            if rec.ready_production_count > 0:
                if rec.production_ids.filtered(lambda r: r.state != "done"):
                    rec.state = "in_progress"
                else:
                    rec.state = "done"
            else:
                rec.state = "draft"

    # TODO: Rename to operation_type_id
    operation_type = fields.Many2one(
        comodel_name="stock.picking.type",
        required=True,
    )

    product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_product_ids",
        string="Products",
    )

    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = rec.production_ids.product_id

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

    def action_check(self):
        self.ensure_one()
        productions = self.production_ids.filtered(lambda r: not r.is_ready_to_produce)
        init_production_count = len(productions)
        productions.action_produce_batch()
        final_production_count = len(
            self.production_ids.filtered(lambda r: not r.is_ready_to_produce)
        )
        if final_production_count and init_production_count == final_production_count:
            message = [
                _("The following productions could not be marked as 'done':"),
                "\n".join(productions.mapped("display_name")),
            ]
            raise UserError("\n".join(message))

    def _check_unique_serial_lot_in_batch(self):
        for rec in self:
            lot_production_map = {}
            for production in rec.production_ids:
                for move_line in production.move_raw_ids.filtered(
                    lambda x: x.product_id.tracking == "serial"
                ).move_line_ids:
                    lot_id = move_line.lot_id.id
                    if lot_id in lot_production_map:
                        dup_production, dup_product = lot_production_map[lot_id]
                        raise ValidationError(
                            _(
                                "The following productions [%s, %s] are using the "
                                "component %s with the same serial number. Please "
                                "make sure that the serial numbers are unique."
                            )
                            % (
                                dup_production.display_name,
                                production.display_name,
                                dup_product.display_name,
                            )
                        )
                    lot_production_map[lot_id] = (production, move_line.product_id)

    def action_done(self):
        self.ensure_one()
        self.action_check()
        self._check_unique_serial_lot_in_batch()
        for production in self.with_context(
            mrp_production_batch_create=True
        ).production_ids:
            production.action_generate_batch_serial()
            production.button_mark_done()

    def _get_common_action_view_production(self):
        tree_view = self.env.ref("mrp_production_batch.mrp_production_tree_view")
        form_view = self.env.ref("mrp_production_batch.mrp_production_form_view")
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

    def action_view_production_ready(self):
        self.ensure_one()
        action = self._get_common_action_view_production()
        action["domain"] = [("id", "in", self.ready_production_ids.ids)]
        return action

    def get_user_locale_tz_datetime_string(self, date):
        self.ensure_one()
        lang = self.env["res.lang"].search([("code", "=", self.env.user.lang)])
        datetime_format = " ".join(
            filter(
                None,
                map(
                    lambda x: x and x.strip() or None,
                    [lang.time_format, lang.date_format],
                ),
            )
        )
        return fields.Datetime.context_timestamp(self, date).strftime(datetime_format)

    @api.depends("name", "state")
    def name_get(self):
        result = []
        for rec in self:
            if rec.state == "draft":
                state = _("Draft")
                user_datetime = rec.get_user_locale_tz_datetime_string(rec.create_date)
                name = "%s [%s] %s" % (
                    state,
                    user_datetime,
                    rec.operation_type.display_name,
                )
            else:
                name = rec.name
            result.append((rec.id, name))
        return result
