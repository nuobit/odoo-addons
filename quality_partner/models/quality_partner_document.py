# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class QualityPartnerDocument(models.Model):
    _name = "quality.partner.document"
    _description = "Quality Partner Document"
    _order = "partner_id,date desc,document_type_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", ondelete="cascade"
    )

    partner_quality_classification_id = fields.Many2one(
        related="partner_id.quality_classification_id", readonly=True
    )

    partner_class_mandatory_document_type_ids = fields.One2many(
        comodel_name="quality.partner.document.type",
        compute="_compute_partner_class_mandatory_document_type_ids",
        readonly=True,
    )

    document_type_id = fields.Many2one(
        comodel_name="quality.partner.document.type",
        string="Document type",
        required=True,
        domain="[('id', 'in', partner_quality_classification_id.document_type_ids.ids)]",
        ondelete="restrict",
    )

    datas = fields.Binary(string="File", attachment=True, required=True)
    datas_fname = fields.Char(string="Filename", required=True)

    date = fields.Date(string="Date", required=True)

    description = fields.Text(string="Description")

    @api.depends("partner_quality_classification_id")
    def _compute_partner_class_mandatory_document_type_ids(self):
        for rec in self:
            rec.partner_class_mandatory_document_type_ids = (
                rec.partner_id.quality_classification_id.mandatory_document_type_ids
            )
