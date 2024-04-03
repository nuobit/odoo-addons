# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eatones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("tracking")
    def _check_tracking_by_lot_id(self):
        for rec in self:
            self.env["stock.move.line"].sudo().search(
                [
                    (
                        "product_id",
                        "in",
                        rec.with_context(active_test=False).product_variant_ids.ids,
                    ),
                ]
            )._check_lot_id_by_tracking()
