# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type = fields.Selection(
        [("consu", "Consumable"), ("service", "Service")],
        string="Product Type",
        readonly=True,
    )

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """, t.type"""
        return res

    def _select_additional_fields(self, fields):
        fields["type"] = ", t.type as type"
        return super()._select_additional_fields(fields)
