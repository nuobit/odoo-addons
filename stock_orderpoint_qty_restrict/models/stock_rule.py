# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id=company_id)
        return domain + [("qty_to_order", ">", 0.0)]
