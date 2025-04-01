# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PartnerDocumentTemplateFile(models.Model):
    _name = "partner.document.template.file"
    _inherit = ["partner.document.template.file", "portal.mixin"]

    # portal.mixin override to download the template from the get_portal_url
    def _compute_access_url(self):
        res = super()._compute_access_url()
        for rec in self:
            rec.access_url = f"/my/documents/template/{rec.id}"
        return res
