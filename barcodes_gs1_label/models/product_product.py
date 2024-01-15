# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def print_gs1_barcode_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "barcodes_gs1_label.barcodes_product_option_wizard_view_action"
        )
        return action

    @api.constrains("barcode")
    def _check_barcode(self):
        for rec in self:
            lot = rec.env["stock.production.lot"].search(
                [("product_id", "=", rec.id), ("gs1_generated", "=", True)],
            )
            if lot:
                raise ValidationError(
                    _(
                        "Exists a lot %s with a GS1 generated, the "
                        "barcode cannot be modified" % lot.mapped("name")
                    )
                )
