# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type = fields.Selection(
        [("consu", "Consumable"), ("service", "Service")],
        string="Product Type",
        readonly=True,
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        fields = {
            **fields,
            "type": ",t.type",
        }
        groupby += ",t.type"

        res = super(SaleReport, self)._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )

        return res
