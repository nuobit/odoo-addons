from datetime import date

from odoo import fields, models


class PartnerDocumentExpiredWizard(models.TransientModel):
    _name = "partner.document.expired.wizard"
    _description = "Partner expired document wizard"

    document_type_ids = fields.Many2many(
        comodel_name="partner.document.type",
        relation="partner_document_expired_wizard_document_type_rel",
        column1="document_expired_wizard_id",
        column2="document_type_id",
        required=True,
        ondelete="restrict",
    )

    date_from = fields.Date()

    date_to = fields.Date(
        required=True,
    )

    def search_expired_documents(self):
        self.ensure_one()
        partner_ids = (
            self.env["partner.document"]
            .search(
                [
                    ("document_type_id", "in", self.document_type_ids.ids),
                    ("datas", "!=", False),
                    ("expiration_date", ">=", self.date_from or date.min),
                    ("expiration_date", "<=", self.date_to),
                ]
            )
            .partner_id.ids
        )
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_partner_form")
        action["domain"] = [("id", "in", partner_ids)]
        action["view_mode"] = self.env.context.get("view", "kanban")
        if action["view_mode"] == "tree":
            for view_id, view_type in action.get("views", []):
                if view_type == "tree":
                    action["views"] = [(view_id, view_type)]
                    break
        return action
