# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductImage(models.Model):
    _inherit = "product.image"

    title = fields.Char()
    alternate_text = fields.Text()

    def _get_seo_meta_data(self):
        self.ensure_one()
        return {
            "title": self.title,
            "alternate_text": self.alternate_text,
        }

    def write(self, vals):
        if "image_1920" in vals:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "image_1920"),
                ]
            )
            attachment.wordpress_bind_ids.unlink()
        return super().write(vals)
