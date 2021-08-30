# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_cancel(self):
        sales_with_done_pickings = self.picking_ids.filtered(
            lambda p: p.state == "done"
        ).mapped("sale_id")
        documents = None
        for sale_order in sales_with_done_pickings:
            if sale_order.state == "sale" and sale_order.order_line:
                sale_order_lines_quantities = {
                    order_line: (order_line.product_uom_qty, 0)
                    for order_line in sale_order.order_line
                }
                documents = self.env["stock.picking"]._log_activity_get_documents(
                    sale_order_lines_quantities, "move_ids", "UP"
                )
        sales_with_done_pickings.with_context(
            from_order=True
        ).picking_ids.action_cancel()
        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if parent._name == "stock.picking":
                    if parent.state == "cancel":
                        continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_decrease_ordered_quantity(filtered_documents, cancel=True)
        return super(SaleOrder, self.with_context(from_order=True))._action_cancel()
