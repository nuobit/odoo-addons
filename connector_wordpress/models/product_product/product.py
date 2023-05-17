# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        if "image_1920" in vals:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "image_variant_1920"),
                ]
            )
            if attachment:
                self.env["wordpress.ir.attachment"].search(
                    [("odoo_id", "=", attachment.id)]
                ).unlink()
        return super().write(vals)
