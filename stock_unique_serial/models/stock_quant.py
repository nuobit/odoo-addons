# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("quantity")
    def check_quantity(self):
        if self.env.context.get("skip_check_quantity", False):
            return
        super().check_quantity()
        for quant in self.filtered(
            lambda x: x.lot_id
            and x.product_id.tracking == "serial"
            and float_compare(
                x.quantity,
                0,
                precision_rounding=x.product_uom_id.rounding,
            )
            > 0
        ):
            available_quantity = sum(
                quant.lot_id.quant_ids.filtered(
                    lambda x: float_compare(
                        x.quantity,
                        0,
                        precision_rounding=quant.product_uom_id.rounding,
                    )
                    > 0
                ).mapped("quantity")
            )
            if available_quantity > 1:
                raise ValidationError(
                    _(
                        "The serial number has already been assigned: \n "
                        "Product: %s, Serial Number: %s"
                    )
                    % (quant.product_id.display_name, quant.lot_id.name)
                )
