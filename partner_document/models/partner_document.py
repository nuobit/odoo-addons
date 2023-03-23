# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PartnerDocument(models.Model):
    _name = "partner.document"
    _description = "Partner Document"
    _order = "partner_id,date desc,document_type_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
    )
    partner_classification_id = fields.Many2one(
        related="partner_id.classification_id",
        readonly=True,
        ondelete="restrict",
    )
    partner_class_mandatory_document_type_ids = fields.One2many(
        comodel_name="partner.document.type",
        compute="_compute_partner_class_mandatory_document_type_ids",
        readonly=True,
    )
    document_type_id = fields.Many2one(
        comodel_name="partner.document.type",
        required=True,
        domain="[('id', 'in', partner_classification_id.document_type_ids.ids)]",
        ondelete="restrict",
    )
    datas = fields.Binary(
        string="File",
        attachment=True,
    )
    datas_fname = fields.Char(
        string="Filename",
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    expiration_date = fields.Date()
    description = fields.Text()

    @api.depends("partner_classification_id")
    def _compute_partner_class_mandatory_document_type_ids(self):
        for rec in self:
            rec.partner_class_mandatory_document_type_ids = (
                rec.partner_id.classification_id.mandatory_document_type_ids
            )
