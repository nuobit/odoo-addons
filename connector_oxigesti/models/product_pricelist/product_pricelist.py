# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def unlink(self):
        for rec in self:
            if rec.item_ids.oxigesti_bind_ids:
                raise ValidationError(
                    _(
                        "You can't delete the pricelist %s that has been exported "
                        "the product prices by customer to Oxigesti. If you want to"
                        "delete it, you must first delete the items of the pricelist."
                    )
                    % rec.name
                )
        return super().unlink()
