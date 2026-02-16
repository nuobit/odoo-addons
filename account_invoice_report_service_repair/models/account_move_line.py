# Copyright 2025 Solutions SL NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_orders(self):
        orders = super()._get_orders()
        if not orders:
            return orders
        repair_orders = self.env["repair.order"].search(
            [("sale_order_id", "in", [o.id for o in orders])]
        )
        if not repair_orders:
            return orders

        sale_to_repair = {ro.sale_order_id.id: ro for ro in repair_orders}
        result_orders = []

        for order in orders:
            if order.id in sale_to_repair:
                result_orders.append(sale_to_repair[order.id])
            else:
                result_orders.append(order)

        return result_orders
