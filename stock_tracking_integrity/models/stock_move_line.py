# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eatones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("product_id", "lot_id", "state")
    def _check_lot_id_by_tracking(self):
        tracking_selection = dict(
            self.fields_get(allfields=["tracking"])["tracking"]["selection"]
        )
        for rec in self:
            if rec.state == "done":
                tracking_label = tracking_selection[rec.product_id.tracking]
                if not rec.lot_id and rec.product_id.tracking != "none":
                    raise ValidationError(
                        _(
                            "The product %s with tracking '%s' only "
                            "can have movements with a lot number."
                        )
                        % (rec.product_id.display_name, tracking_label)
                    )
                if rec.lot_id and rec.product_id.tracking == "none":
                    raise ValidationError(
                        _(
                            "The product %s with tracking '%s' only "
                            "can have movements without a lot number."
                        )
                        % (rec.product_id.display_name, tracking_label)
                    )
