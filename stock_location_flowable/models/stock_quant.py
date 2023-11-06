# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("location_id", "quantity")
    def _check_unique_lot(self):
        for rec in self:
            if not self.env.context.get("allow_duplicate"):
                if rec.location_id.flowable_storage:
                    if (
                        len(
                            rec.product_id.stock_quant_ids.filtered(
                                lambda x: float_compare(
                                    x.quantity,
                                    0,
                                    precision_rounding=rec.product_uom_id.rounding,
                                )
                                > 0
                                and x.location_id == rec.location_id
                            )
                        )
                        > 1
                    ):
                        raise ValidationError(
                            _(
                                "You cannot have more than one"
                                " lot in the same location."
                            )
                        )
