# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductDocumentMixin(models.AbstractModel):
    _inherit = "product.document"

    def write(self, vals):
        if "datas" in vals:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "datas"),
                ]
            )
            attachment.wordpress_bind_ids.unlink()
        return super().write(vals)
