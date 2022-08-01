# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.constrains("removal_date", "use_expiration_date")
    def _check_required_removal_date(self):
        for rec in self:
            if rec.use_expiration_date and not rec.removal_date:
                raise ValidationError(
                    _("Removal date is required for this product %s")
                    % rec.product_id.display_name
                )
