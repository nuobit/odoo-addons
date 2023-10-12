# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerDocument(models.Model):
    _name = "partner.document"
    _description = "Partner Document"
    _order = "partner_id, partner_classification_id, document_type_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
    )
    partner_classification_id = fields.Many2one(
        comodel_name="partner.classification",
        compute="_compute_partner_classification_id",
        store=True,
        ondelete="restrict",
    )

    @api.depends("document_type_id")
    def _compute_partner_classification_id(self):
        for rec in self:
            rec.partner_classification_id = rec.partner_id.classification_id

    partner_class_mandatory_document_type_ids = fields.One2many(
        comodel_name="partner.document.type",
        compute="_compute_partner_class_mandatory_document_type_ids",
        readonly=True,
    )

    @api.depends("partner_classification_id")
    def _compute_partner_class_mandatory_document_type_ids(self):
        for rec in self:
            rec.partner_class_mandatory_document_type_ids = (
                rec.partner_id.classification_id.mandatory_document_type_ids
            )

    document_type_id = fields.Many2one(
        comodel_name="partner.document.type",
        required=True,
        domain="[('id', 'in', partner_classification_id.document_type_ids.ids)]",
        ondelete="restrict",
    )

    datas = fields.Binary(
        string="File",
        attachment=True,
    )
    datas_fname = fields.Char(
        string="Filename",
    )

    expiration_date = fields.Date()
    description = fields.Text()

    expired = fields.Boolean(
        compute="_compute_expired",
    )

    @api.depends("expiration_date", "datas")
    def _compute_expired(self):
        for rec in self:
            rec.expired = (
                rec.datas
                and rec.expiration_date
                and rec.expiration_date < fields.Date.today()
            )

    def write(self, vals):
        for rec in self:
            if "document_type_id" in vals:
                if vals["document_type_id"] != rec.document_type_id:
                    if rec.datas:
                        _(
                            "You can't change the %(document_type)s "
                            "(%(classification)s) if it has a File"
                        ) % {
                            "document_type": rec.document_type_id.display_name,
                            "classification": rec.partner_classification_id.display_name,
                        }

        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.datas:
                raise ValidationError(
                    _(
                        "You can't delete %(document_type)s (%(classification)s)"
                        " because it has a File"
                    )
                    % {
                        "document_type": rec.document_type_id.display_name,
                        "classification": rec.partner_classification_id.display_name,
                    }
                )
            if rec.partner_id.classification_id:
                docs = self.env[self._name].search(
                    [
                        ("partner_id", "=", rec.partner_id.id),
                        (
                            "partner_classification_id",
                            "=",
                            rec.partner_classification_id.id,
                        ),
                        ("datas", "!=", False),
                    ]
                )
                if (
                    docs
                    and rec.document_type_id
                    in rec.partner_class_mandatory_document_type_ids
                ):
                    raise ValidationError(
                        _(
                            "You cannot delete %(document_type)s because it is required"
                            " in (%(classification)s). If you want to delete it, you "
                            "must delete the files of the rest of the document types of"
                            " this classification"
                        )
                        % {
                            "document_type": rec.document_type_id.display_name,
                            "classification": rec.partner_classification_id.display_name,
                        }
                    )
        return super().unlink()
