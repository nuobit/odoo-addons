# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_main_tasks(self):
        tasks_ids = super(SaleOrder, self)._prepare_main_tasks()
        return tasks_ids.filtered(lambda x: not x.sale_line_id.pack_parent_line_id)

    def _prepare_other_tasks_duration(self, tasks):
        filtered_tasks = tasks.browse()
        for t in tasks:
            pack_parent_product_template = (
                t.sale_line_id.pack_parent_line_id.product_id.product_tmpl_id
            )
            if pack_parent_product_template.pack_component_price != "ignored":
                filtered_tasks |= t
        return super(SaleOrder, self)._prepare_other_tasks_duration(filtered_tasks)
