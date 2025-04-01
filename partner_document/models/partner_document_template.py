# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PartnerDocumentTemplate(models.Model):
    _name = "partner.document.template"
    _description = "Partner Document Template"

    name = fields.Char()
    file_ids = fields.One2many(
        comodel_name="partner.document.template.file", inverse_name="template_id"
    )
