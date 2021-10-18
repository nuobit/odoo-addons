# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    alternate_name_description = fields.Char(
        compute="_compute_alternate_name_description"
    )
    alternate_name = fields.Char(compute="_compute_alternate_name")

    @api.depends("partner_id", "name", "bike_location", "alternate_name_description")
    def _compute_alternate_name(self):
        bike_location_mapping = dict(
            self.fields_get("bike_location", "selection")["bike_location"]["selection"]
        )
        for rec in self:
            rec.alternate_name = " ".join(
                filter(
                    None,
                    [
                        rec.partner_id.name,
                        rec.alternate_name_description,
                        rec.name,
                        bike_location_mapping[rec.bike_location],
                    ],
                )
            )

    @api.depends("order_line", "order_line.product_id")
    def _compute_alternate_name_description(self):
        for rec in self:
            rec.alternate_name_description = " ".join(
                rec.order_line.filtered(
                    lambda x: x.product_id.categ_id.is_service_description
                )
                .sorted(
                    lambda x: (
                        x.product_id.product_tmpl_id.service_description_type,
                        x.sequence,
                    )
                )
                .mapped(
                    lambda x: ",".join(x.product_id.attribute_value_ids.mapped("name"))
                )
            )
