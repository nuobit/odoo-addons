# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        self.tasks_ids.write({"sale_line_id": False})
        self.tasks_ids.unlink()
        return super(SaleOrder, self).action_cancel()
