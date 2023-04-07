# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    classification_id = fields.Many2one(
        comodel_name="partner.classification",
        string="Classification",
        ondelete="restrict",
        default=lambda self: self.env["partner.classification"].search(
            [("default", "=", True)], limit=1
        ),
    )
    document_ids = fields.One2many(
        comodel_name="partner.document",
        string="Documents",
        inverse_name="partner_id",
        compute="_compute_document_ids",
        store=True,
        readonly=False,
    )

    @api.depends("classification_id", "classification_id.document_type_ids")
    def _compute_document_ids(self):
        doc_types = []
        for rec in self:
            for doc_type in rec.document_ids:
                if (
                    doc_type.document_type_id
                    not in rec.classification_id.document_type_ids
                    and not doc_type.datas
                ):
                    doc_types += [(2, doc_type.id, 0)]
            for doc_type in rec.classification_id.document_type_ids:
                if not rec.document_ids.filtered(
                    lambda x: x.document_type_id == doc_type
                ) or rec.document_ids.filtered(
                    lambda x: x.document_type_id == doc_type
                    and x.expiration_date
                    and x.expiration_date < fields.Date.today()
                ):
                    doc_types += [(0, 0, {"document_type_id": doc_type.id})]
            rec.document_ids = doc_types

    remain_files = fields.Boolean(
        compute="_compute_remain_files",
    )

    @api.depends("document_ids", "classification_id")
    def _compute_remain_files(self):
        for rec in self:
            rec.remain_files = False
            for type in rec.classification_id.document_type_ids:
                valid_document = rec.document_ids.filtered(
                    lambda x: x.document_type_id == type
                    and x.expiration_date
                    and x.expiration_date > fields.Date.today()
                    and x.datas
                )
                if not valid_document:
                    rec.remain_files = True
                    break

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        default_classification = self.env["partner.classification"].search(
            [("default", "=", True)], limit=1
        )
        if default_classification:
            defaults["classification_id"] = default_classification.id
        return defaults

    # @api.constrains("quality_classification_id", "quality_document_ids")
    # def _check_classification_document_type(self):
    #     for rec in self:
    #         if not rec.quality_classification_id:
    #             if rec.quality_document_ids:
    #                 raise ValidationError(
    #                     _(
    #                         "If there's documents submitted, "
    #                         "the classification can not be null"
    #                     )
    #                 )
    #         else:
    #             if rec.quality_document_ids:
    #                 mandatory_document_ids = (
    #                     rec.quality_classification_id.mandatory_document_type_ids
    #                 )
    #                 submitted_document_ids = rec.quality_document_ids.mapped(
    #                     "document_type_id"
    #                 )
    #                 if mandatory_document_ids - submitted_document_ids:
    #                     raise ValidationError(
    #                         _("Not all mandatory document types are submitted")
    #                     )
    #                 if submitted_document_ids - mandatory_document_ids:
    #                     raise ValidationError(
    #                         _(
    #                             "There're documents submitted that are not "
    #                             "mandatory for the classification selected"
    #                         )
    #                     )
