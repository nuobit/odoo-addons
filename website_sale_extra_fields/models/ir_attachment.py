# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    checksum_id = fields.Many2one(
        comodel_name="ir.checksum",
        compute="_compute_checksum_id",
    )

    @api.model
    def _get_checksum_id(self, checksum):
        return self.env["ir.checksum"].search(
            [
                ("checksum", "=", checksum),
            ],
        )

    @api.depends("checksum")
    def _compute_checksum_id(self):
        for rec in self:
            checksum = self._get_checksum_id(rec.checksum)
            if not checksum:
                checksum = self.env["ir.checksum"].create(
                    {
                        "checksum": rec.checksum,
                    }
                )
            rec.checksum_id = checksum
