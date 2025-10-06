# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eatones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "lot_id", "quantity")
    def _check_lot_id_by_tracking(self):
        tracking_selection = dict(
            self.env["product.template"].fields_get(allfields=["tracking"])["tracking"][
                "selection"
            ]
        )
        for rec in self.filtered(lambda q: q.quantity > 0):
            tracking_label = tracking_selection.get(
                rec.product_id.tracking, rec.product_id.tracking
            )
            if not rec.lot_id and rec.product_id.tracking != "none":
                raise ValidationError(
                    _(
                        "The product %(product_name)s with tracking "
                        "'%(tracking)s' only "
                        "can have quants with a lot number."
                    )
                    % {
                        "product_name": rec.product_id.display_name,
                        "tracking": tracking_label,
                    }
                )
            if rec.lot_id and rec.product_id.tracking == "none":
                raise ValidationError(
                    _(
                        "The product %(product_name)s with tracking "
                        "'%(tracking)s' only "
                        "can have quants without a lot number."
                    )
                    % {
                        "product_name": rec.product_id.display_name,
                        "tracking": tracking_label,
                    }
                )
