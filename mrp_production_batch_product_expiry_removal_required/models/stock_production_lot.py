# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.constrains("removal_date", "use_expiration_date")
    def _check_required_removal_date(self):
        if not self.env.context.get("skip_removal_date_check"):
            super()._check_required_removal_date()

    def _get_dates(self, product_id=None):
        if self.env.context.get("mrp_production_batch_create"):
            product = self.env["product.product"].browse(product_id) or self.product_id
            if not product.removal_time:
                raise ValidationError(
                    _(
                        "Product %s requires a removal time to generate production "
                        "batches.  Please set it before continuing."
                    )
                    % product.display_name
                )
        return super()._get_dates(product_id=product_id)
