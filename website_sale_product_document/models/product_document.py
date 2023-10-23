# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductDocument(models.AbstractModel):
    _name = "product.document"
    _description = "Product Document"
    _order = "sequence, id"

    sequence = fields.Integer()
    name = fields.Char(
        translate=True,
        required=True,
    )
    datas = fields.Binary(
        string="Attachment",
        attachment=True,
        required=True,
    )
    datas_fname = fields.Char(string="Filename")
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        compute="_compute_attachment_id",
    )

    @api.depends("datas")
    def _compute_attachment_id(self):
        for rec in self:
            attachment = rec.env["ir.attachment"].search(
                [
                    ("res_field", "=", "datas"),
                    ("res_id", "=", rec.id),
                    ("res_model", "=", rec._name),
                ]
            )
            if not attachment:
                raise ValidationError(_("No attachment found"))
            elif len(attachment) > 1:
                raise ValidationError(_("More than one attachment found"))
            else:
                rec.attachment_id = attachment[0]
