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

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        fields = fields or {}
        fields["type"] = ", t.type as type"
        groupby += ", t.type"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
