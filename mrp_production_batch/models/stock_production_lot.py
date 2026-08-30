# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if rec.name == "" and not self.env.context.get(
                "mrp_production_batch_create"
            ):
                raise ValidationError(_("This name is reseved for internal use."))
