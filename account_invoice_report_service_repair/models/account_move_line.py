# Copyright 2025 Solutions SL NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_orders(self):
        """Get related orders including repair orders.

        In Odoo 18, repair orders are linked to invoices through sale orders.
        The fields repair_fee_ids and repair_line_ids no longer exist.

        Returns repair.order if exists, otherwise returns sale.order.
        This ensures one line belongs to only one order.
        """
        orders = super()._get_orders()
        sale_order_ids = [order.id for order in orders]

        if sale_order_ids:
            # Find repair orders linked to those sale orders
            repair_orders = self.env["repair.order"].sudo().search(
                [("sale_order_id", "in", sale_order_ids)]
            )

            # Replace sale orders with their repair orders to avoid duplicates
            if repair_orders:
                # Create mapping of sale_order_id -> repair_order
                sale_to_repair = {ro.sale_order_id.id: ro for ro in repair_orders}

                # Replace sale orders with repair orders when they exist
                result_orders = []
                for order in orders:
                    if order.id in sale_to_repair:
                        result_orders.append(sale_to_repair[order.id])
                    else:
                        result_orders.append(order)
                return result_orders

        return orders
