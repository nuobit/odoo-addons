# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

from odoo import api, fields, models


class ProductImage(models.Model):
    _inherit = "product.image"

    raw_checksum_id = fields.Many2one(
        comodel_name="ir.checksum",
        compute="_compute_raw_checksum_id",
        store=True,
    )

    @api.depends("image_1920", "image_1024")
    def _compute_raw_checksum_id(self):
        for rec in self:
            if rec.image_1920 or rec.image_1024:
                checksum = self.env["ir.attachment"]._compute_checksum(
                    base64.b64decode(rec.image_1920)
                )
                raw_checksum = self.env["ir.checksum"].search(
                    [
                        ("checksum", "=", checksum),
                    ],
                )
                if not raw_checksum:
                    # This create is a workaround when image is modified
                    # in view and attachment it hasn't been created nor modified yet
                    raw_checksum = self.env["ir.checksum"].create(
                        {
                            "checksum": checksum,
                        }
                    )
                rec.raw_checksum_id = raw_checksum
            else:
                rec.raw_checksum_id = False

    title = fields.Char(
        related="raw_checksum_id.title",
        readonly=False,
    )
    alternate_text = fields.Text(
        related="raw_checksum_id.alternate_text",
        readonly=False,
    )
