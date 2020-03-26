# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    quality_classification_id = fields.Many2one(comodel_name='quality.partner.classification',
                                                string='Classification',
                                                domain=[('level_type', '=', 'description')],
                                                on_delete='restrict')
    quality_document_ids = fields.One2many(comodel_name='quality.partner.document',
                                           string='Documents',
                                           inverse_name='partner_id')

    @api.constrains('quality_classification_id', 'quality_document_ids',
                    'quality_document_ids.document_type_id')
    def _check_classification_document_type(self):
        for rec in self:
            if not rec.quality_classification_id:
                if rec.quality_document_ids:
                    raise ValueError(_("If there's documents submitted, the classification can not be null"))
            else:
                if rec.quality_document_ids:
                    mandatory_document_ids = rec.quality_classification_id.mandatory_document_type_ids
                    submitted_document_ids = rec.quality_document_ids.mapped('document_type_id')
                    if mandatory_document_ids - submitted_document_ids:
                        raise ValueError(_("Not all mandatory document types are submitted"))
                    if submitted_document_ids - mandatory_document_ids:
                        raise ValueError(
                            _("There're documents submitted that are not mandatory for the classification selected"))
