# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id=company_id)
        return domain + [("qty_to_order", ">", 0.0)]
