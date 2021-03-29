# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_main_tasks(self):
        tasks_ids = super(SaleOrder, self)._prepare_main_tasks()
        return tasks_ids.filtered(lambda x: not x.sale_line_id.pack_parent_line_id)
