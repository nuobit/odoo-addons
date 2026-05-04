# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_default_classification_id(self):
        return self.env["partner.classification"].search(
            [("default", "=", True)], limit=1
        )

    classification_id = fields.Many2one(
        comodel_name="partner.classification",
        string="Classification",
        ondelete="restrict",
        default=lambda self: self._get_default_classification_id(),
    )
    document_ids = fields.One2many(
        comodel_name="partner.document",
        string="Documents",
        inverse_name="partner_id",
        compute="_compute_document_ids",
        store=True,
        readonly=False,
    )
    remain_files = fields.Boolean(
        compute="_compute_remain_files",
    )
    document_count = fields.Integer(
        compute="_compute_document_count",
    )

    def _get_valid_document(self, doc_type):
        return self.document_ids.filtered(
            lambda x: x.document_type_id == doc_type and x.is_valid_document()
        )

    @api.depends("document_ids", "classification_id")
    def _compute_remain_files(self):
        for rec in self:
            rec.remain_files = False
            for doc_type in rec.classification_id.document_type_ids:
                if not self._get_valid_document(doc_type):
                    rec.remain_files = True
                    break

    @api.depends("document_ids")
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    def action_view_partner_documents(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "partner_document.action_partner_document_partner"
        )
        action["res_id"] = self.id
        return action

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
