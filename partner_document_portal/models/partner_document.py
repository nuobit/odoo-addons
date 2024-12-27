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
