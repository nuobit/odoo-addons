# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PartnerDocument(models.Model):
    _name = "partner.document"
    _inherit = ["partner.document", "portal.mixin"]

    # portal.mixin override
    def _compute_access_url(self):
        res = super()._compute_access_url()
        for document in self:
            document.access_url = f"/my/documents/{document.id}"
        return res

    def get_template_file_by_lang(self):
        lang = self.env.context.get("lang")
        if not lang:
            lang = self.env.user.lang
        template_file = self.document_type_id.template_id.file_ids.filtered(
            lambda x: x.lang_id.code == lang
        )
        if not template_file:
            template_file = self.document_type_id.template_id.file_ids.filtered(
                lambda x: x.default
            )
        return template_file
