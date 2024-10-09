# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_price_total_and_subtotal_model(
        self,
        price_unit,
        quantity,
        discount,
        currency,
        product,
        partner,
        taxes,
        move_type,
    ):
        res = super()._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )
        if (
            self.move_id.partner_id.service_intermediary
            and self.sale_line_ids
            and self.price_subtotal
            and self.price_total
        ):
            res["price_subtotal"] = self.price_subtotal
            res["price_total"] = self.price_total
        return res

    service_group = fields.Boolean()
