# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Modelo para los archivos asociados a una plantilla de documento.
"""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DocumentTemplateFile(models.Model):
    _name = "document.template.file"
    _description = "Document Template File"
    _order = "default desc"

    template_id = fields.Many2one(
        comodel_name="document.template", required=True, string="Template"
    )
    default = fields.Boolean()
    lang_id = fields.Many2one(comodel_name="res.lang", required=True, string="Language")
    datas = fields.Binary(required=True, string="File")
    datas_fname = fields.Char(string="Filename")

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                if self.search_count(
                    [
                        ("id", "!=", rec.id),
                        ("default", "=", True),
                        ("template_id", "=", rec.template_id.id),
                    ]
                ):
                    raise ValidationError(
                        _("Only one file can be the default."),
                    )

    @api.constrains("lang_id")
    def _check_lang_id(self):
        for rec in self:
            if self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("lang_id", "=", rec.lang_id.id),
                    ("template_id", "=", rec.template_id.id),
                ]
            ):
                raise ValidationError(
                    _("Only one file can set for the same language."),
                )
