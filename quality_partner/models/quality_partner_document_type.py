# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class QualityPartnerDocumentType(models.Model):
    _name = "quality.partner.document.type"
    _description = "Quality Partner Document Type"
    _order = "sequence"

    name = fields.Char(translate=True, required=True)
    code = fields.Char()
    description = fields.Text()
    sequence = fields.Integer(required=True, default=1)

    def unlink(self):
        records = self.env["quality.partner.classification"].search(
            [("document_type_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        records = self.env["quality.partner.document"].search(
            [("document_type_id", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
