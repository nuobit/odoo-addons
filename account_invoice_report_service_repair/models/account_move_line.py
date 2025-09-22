# Copyright 2025 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_orders(self):
        # we use a list to allow different types of orders, sale, repair, etc
        return super()._get_orders() + [
            order
            for order in (
                self.sudo().repair_fee_ids.repair_id
                | self.sudo().repair_line_ids.repair_id
            )
        ]
