# Copyright NuoBiT Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# Copyright NuoBiT 2025 - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerDocument(models.Model):
    _name = "partner.document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
        ondelete="restrict",
    )

    @api.onchange("partner_classification_id")
    def _onchange_domain_document_type_id(self):
        domain = []
        if self.partner_id.classification_id:
            domain = [
                ("id", "in", self.partner_id.classification_id.document_type_ids.ids)
            ]
        return {"domain": {"document_type_id": domain}}

    datas = fields.Binary(
        string="File",
        attachment=True,
    )
    datas_fname = fields.Char(
        string="Filename",
    )

    expiration_date = fields.Date(
        compute="_compute_expiration_date",
        store=True,
        readonly=False,
    )

    @api.depends("datas")
    def _compute_expiration_date(self):
        for rec in self:
            if not rec.datas:
                rec.expiration_date = False

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

    validated = fields.Boolean(
        compute="_compute_validated",
        store=True,
        readonly=False,
        default=False,
        tracking=True,
    )

    @api.depends("datas", "expiration_date")
    def _compute_validated(self):
        for rec in self:
            if rec.validated:
                rec.validated = False

    no_expiration = fields.Boolean(related="document_type_id.no_expiration")

    @api.constrains("expiration_date", "document_type_id")
    def _check_expiration_date_by_type(self):
        for rec in self:
            if rec.document_type_id.no_expiration and rec.expiration_date:
                raise ValidationError(
                    _(
                        "You cannot set an expiration date for a 'No Expiration' "
                        "document type."
                    )
                )

    def write(self, vals):
        res = super().write(vals)
        self._validate_document()
        return res

    def _validate_document(self):
        for rec in self:
            datas = rec.datas
            document_type = rec.document_type_id
            expiration_date = rec.expiration_date

            if datas and not document_type.no_expiration and not expiration_date:
                raise ValidationError(_("Expiration date is required for this file"))

            if rec.document_type_id != document_type:
                raise ValidationError(
                    _(
                        "You can't change the %(document_type)s "
                        "(%(classification)s) if it has a File"
                    )
                    % {
                        "document_type": rec.document_type_id.display_name,
                        "classification": rec.partner_classification_id.display_name,
                    }
                )

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._validate_document()
        return res

    def unlink(self):
        for rec in self:
            # Temporarily disabled – raises error even without file
            # if rec.datas:
            #     raise ValidationError(
            #         _(
            #             "You can't delete %(document_type)s (%(classification)s) "
            #             "because it has a File"
            #         )
            #         % {
            #             "document_type": rec.document_type_id.display_name,
            #             "classification": rec.partner_classification_id.display_name,
            #         }
            #     )

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
                            "You cannot delete %(document_type)s "
                            "because it is required "
                            "in (%(classification)s). "
                            "If you want to delete it, you must delete "
                            "the files of the rest of the document"
                            " types of this classification."
                        )
                        % {
                            "document_type": rec.document_type_id.display_name,
                            "classification": rec.partner_classification_id.display_name,
                        }
                    )
        return super().unlink()
