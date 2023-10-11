# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PartnerDocumentType(models.Model):
    _name = "partner.document.type"
    _description = "Partner Document Type"
    _order = "sequence"

    name = fields.Char(
        translate=True,
        required=True,
    )
    # code = fields.Char(string="Code")
    description = fields.Text()
    sequence = fields.Integer(
        required=True,
        default=1,
    )

    @api.constrains("name")
    def _check_name(self):
        for record in self:
            if self.env[self._name].search_count(
                [("id", "!=", record.id), ("name", "=ilike", record.name)]
            ):
                raise ValidationError(
                    _("The name must be unique!"),
                )

    def unlink(self):
        records = self.env["partner.classification"].search(
            [("document_type_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        records = self.env["partner.document"].search(
            [("document_type_id", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(PartnerDocumentType, self).unlink()
