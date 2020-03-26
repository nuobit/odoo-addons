# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _


class QualityPartnerDocument(models.Model):
    _name = 'quality.partner.document'
    _order = 'partner_id,date desc,document_type_id'

    document_type_id = fields.Many2one(comodel_name='quality.partner.document.type',
                                       string='Document type', required=True,
                                       domain="[('id', 'in', quality_classification_id.document_type_ids)]",
                                       on_delete='restrict')

    datas = fields.Binary(string="File", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)

    date = fields.Date(string='Date', required=True)

    description = fields.Text(string='Description')

    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner',
                                 on_delete='cascade')

    partner_quality_classification_id = fields.Many2one(related='partner_id.quality_classification_id', readonly=True)

    partner_class_mandatory_document_type_ids = fields.One2many(comodel_name='quality.partner.document.type',
                                                                compute="_partner_class_mandatory_document_type_ids",
                                                                readonly=True)

    @api.depends('partner_quality_classification_id')
    def _partner_class_mandatory_document_type_ids(self):
        for rec in self:
            rec.partner_class_mandatory_document_type_ids = rec.partner_id.quality_classification_id.mandatory_document_type_ids
