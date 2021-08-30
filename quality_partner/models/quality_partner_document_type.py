# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class QualityPartnerDocumentType(models.Model):
    _name = "quality.partner.document.type"
    _order = "sequence"

    name = fields.Char(string="Name", translate=True, required=True)
    code = fields.Char(string="Code")

    description = fields.Text(string="Description")
    sequence = fields.Integer(string="Sequence", required=True, default=1)

    @api.multi
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

        return super(QualityPartnerDocumentType, self).unlink()
