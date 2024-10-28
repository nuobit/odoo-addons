# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductImage(models.Model):
    _inherit = "product.image"

    image_1920 = fields.Image(required=False)

    @api.constrains("video_url", "image_1920")
    def _check_image_1920(self):
        for rec in self:
            if not rec.video_url and not rec.image_1920:
                raise ValidationError(
                    _(
                        "It is mandatory to provide the video URL for the additional "
                        "media of product %s if you want to leave the image blank."
                    )
                    % rec.name
                )
