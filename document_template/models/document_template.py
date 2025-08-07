# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Modelo principal para plantillas de documentos.
"""
from odoo import fields, models


class DocumentTemplate(models.Model):
    _name = "document.template"
    _description = "Document Template"

    name = fields.Char(required=True)
    file_ids = fields.One2many(
        comodel_name="document.template.file",
        inverse_name="template_id",
        string="Files",
    )
