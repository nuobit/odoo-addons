# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        meta_type = {
            ("draft", "open"): "done",
            ("open", "paid"): "parking",
        }.get((self.state, vals.get("state")))
        if meta_type:
            default_deposit_product_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("sale.default_deposit_product_id")
            )
            for rec in self:
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
        return super(AccountInvoice, self).write(vals)

    @api.model
    def archive_paid_invoices(self, days=10):
        invoices = self.env["account.move"].search(
            [
                ("state", "=", "paid"),
            ]
        )
        _logger.info(
            "Archiving tasks of %i invoices paid %i days ago..." % (len(invoices), days)
        )
        archived = 0
        for invoice in invoices:
            last_payment_date = datetime.date(1900, 1, 1)
            payment_ids = invoice.payment_ids.sorted("payment_date")
            if payment_ids:
                last_payment_date = payment_ids[-1].payment_date
            for order in invoice.mapped("invoice_line_ids.sale_line_ids.order_id"):
                for task in order.tasks_ids.filtered("active"):
                    if (datetime.date.today() - last_payment_date).days >= days:
                        task.toggle_active()
                        archived += 1
        _logger.info(
            "Archived %i tasks of %i invoices paid %i days ago..."
            % (archived, len(invoices), days)
        )
