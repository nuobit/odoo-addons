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
        for rec in self:
            selected_docs = rec.document_ids.filtered(
                lambda x: x.partner_classification_id == rec.classification_id
            ).document_type_id
            rest_docs = rec.document_ids.filtered(
                lambda x: x.partner_classification_id != rec.classification_id
            )
            actions = []

            # # DELETE DOCUMENTS
            for cd in rest_docs.mapped("partner_classification_id"):
                docs = rest_docs.filtered(lambda x: x.partner_classification_id == cd)
                if not any(docs.filtered(lambda x: x.datas)):
                    actions += [(2, dc.id, 0) for dc in docs]

            # CREATE NEW DOCUMENTS
            new_docs = rec.classification_id.document_type_ids - selected_docs
            for doc_type in new_docs:
                vals = {
                    "partner_id": rec._origin.id,
                    "partner_classification_id": rec.classification_id.id,
                    "document_type_id": doc_type.id,
                }
                actions.append((0, 0, vals))

            rec.document_ids = actions

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
