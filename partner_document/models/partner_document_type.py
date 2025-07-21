# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models, re
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
    classification_ids = fields.Many2many(
        comodel_name="partner.classification",
        relation="partner_classification_document_type_rel",
        column1="document_type_id",
        column2="classification_id",
        readonly=True,
    )
    partner_count = fields.Integer(
        compute="_compute_partner_count",
        help="Number of distinct partners with documents of this type.",
    )

    def _compute_partner_count(self):
        for record in self:
            record.partner_count = self.env["res.partner"].search_count(
                [("document_ids.document_type_id", "=", record.id)]
            )

    @api.constrains("name")
    def _check_name(self):
        records = self.search([])
        slugs = {}

        for r in records:
            name = r.name.lower().strip()
            for pat, rep in self.get_name_normalization_rules():
                name = name.replace(pat, rep)
            name = re.sub(r"[\s_]+", "-", name)
            name = re.sub(r"[^a-z0-9-]", "", name)
            name = re.sub(r"-+", "-", name)
            slugs[r.id] = name

        for rec in self:
            slug_actual = slugs[rec.id]
            for other_id, slug_otro in slugs.items():
                if other_id == rec.id:
                    continue
                if slug_actual == slug_otro:
                    raise ValidationError(
                        _("There is another document type with a similar name.")
                    )

    def get_name_normalization_rules(self):
        return [
            (" de ", " "),
            ("ss", "s"),
        ]

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
