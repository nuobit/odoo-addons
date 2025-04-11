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
    template_id = fields.Many2one(comodel_name="partner.document.template")
    no_expiration = fields.Boolean(
        default=False,
        help="Check this if the document type does not require an expiration date.",
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

    @api.constrains("template_id")
    def _check_template_id(self):
        for rec in self:
            if rec.template_id:
                if not rec.template_id.file_ids.filtered(lambda x: x.default):
                    raise ValidationError(
                        _("To assign a template, you must first set a default file.")
                    )

    def write(self, vals):
        for rec in self:
            if "no_expiration" in vals and vals["no_expiration"] is False:
                docs_without_exp = self.env["partner.document"].search(
                    [("document_type_id", "=", rec.id), ("expiration_date", "=", False)]
                )
                if docs_without_exp:
                    raise ValidationError(
                        _(
                            "Cant 'uncheck 'No Expiration' due to docs without expiration date"
                        )
                    )
        return super().write(vals)

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
