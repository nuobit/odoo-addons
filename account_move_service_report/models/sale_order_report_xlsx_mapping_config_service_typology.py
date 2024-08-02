# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrderReportXlsxMappingConfigServiceTypology(models.Model):
    _name = "sale.order.report.xlsx.mapping.config.service.typology"
    _description = "Sale Order Report Xlsx Mapping Config Service Typology"

    config_id = fields.Many2one(comodel_name="sale.order.report.xlsx.mapping.config")
    name = fields.Char()
    key = fields.Char()
    transfer_reason = fields.Char()

    @api.constrains("key", "transfer_reason")
    def _check_key_transfer_reason(self):
        for rec in self:
            duplicate = self.config_id.service_typology_ids.filtered(
                lambda x: x.id != rec.id and x.key == rec.key and x.transfer_reason == rec.transfer_reason
            )
            if duplicate:
                raise ValidationError(
                    _("Key and Transfer Reason must be unique in the same configuration.")
                )
