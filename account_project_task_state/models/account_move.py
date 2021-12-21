# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        for rec in self.filtered(lambda r: r.move_type == "out_invoice"):
            if vals.get("payment_state") == "paid":
                new_invoice_state = "paid"
            else:
                new_invoice_state = vals.get("state", rec.state)
            meta_type = {
                ("draft", "posted"): "done",
                ("posted", "paid"): "parking",
            }.get((rec.state, new_invoice_state))
            if meta_type:
                default_deposit_product_id = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("sale.default_deposit_product_id")
                )
                if default_deposit_product_id:
                    if set(rec.invoice_line_ids.mapped("product_id").ids) == {
                        int(default_deposit_product_id)
                    }:
                        continue
                for order in rec.mapped("invoice_line_ids.sale_line_ids.order_id"):
                    for task in order.tasks_ids:
                        task_type = self.env["project.task.type"].search(
                            [
                                ("project_ids", "in", task.project_id.ids),
                                ("meta_type", "=", meta_type),
                            ]
                        )
                        if task_type:
                            if len(task_type) > 1:
                                raise UserError(
                                    _(
                                        "The project '%s' has defined "
                                        "more than one stage %s of type '%s'"
                                    )
                                    % (
                                        task.project_id.name,
                                        task_type.mapped("name"),
                                        meta_type,
                                    )
                                )
                            task.stage_id = task_type.id
        return super(AccountMove, self).write(vals)

    @api.model
    def archive_paid_invoices(self, days=10):
        invoices = self.env["account.move"].search(
            [("payment_state", "=", "paid"), ("move_type", "=", "out_invoice")]
        )
        _logger.info(
            "Archiving tasks of %i invoices paid %i days ago..." % (len(invoices), days)
        )
        archived = 0
        for invoice in invoices:
            last_payment_date = datetime.date(1900, 1, 1)
            payment_items = self.env["account.move.line"].search(
                [
                    ("id", "in", invoice.line_ids._reconciled_lines()),
                    ("move_id", "!=", invoice.id),
                ]
            )

            if payment_items:
                last_payment_date = payment_items.sorted("date")[-1].date
            for order in invoice.mapped("invoice_line_ids.sale_line_ids.order_id"):
                for task in order.tasks_ids.filtered("active"):
                    if (datetime.date.today() - last_payment_date).days >= days:
                        task.toggle_active()
                        archived += 1
        _logger.info(
            "Archived %i tasks of %i invoices paid %i days ago..."
            % (archived, len(invoices), days)
        )
