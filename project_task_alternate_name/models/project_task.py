# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def name_get(self):
        result = []
        for rec in self:
            name = rec.sale_order_id.alternate_name or rec.name
            result.append((rec.id, name))
        return result
