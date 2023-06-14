# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.product_bike_info.models.product_template import BIKE_TYPES


class SaleReport(models.Model):
    _inherit = "sale.report"

    bike_type = fields.Selection(
        selection=BIKE_TYPES,
        string="Bike Type",
        readonly=True,
    )
    is_electric_bike = fields.Boolean(
        string="Bike Electric",
        readonly=True,
    )
    bike_year = fields.Integer(
        string="Bike Year",
        readonly=True,
    )

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """, t.bike_type, t.is_electric_bike, t.bike_year"""
        return res

    def _select_additional_fields(self, fields):
        fields["bike_type"] = ", t.bike_type as bike_type"
        fields["is_electric_bike"] = ", t.is_electric_bike as is_electric_bike"
        fields["bike_year"] = ", t.bike_year as bike_year"
        return super()._select_additional_fields(fields)
