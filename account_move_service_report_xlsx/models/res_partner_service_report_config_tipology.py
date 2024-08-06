# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerServiceReportConfigTypology(models.Model):
    _name = "res.partner.service.report.config.typology"
    _description = "Res Partner Service Report Config Typology"

    config_id = fields.Many2one(comodel_name="res.partner.service.report.config")
    name = fields.Char()
    key = fields.Char()
    transfer_reason = fields.Char()

    @api.constrains("key", "transfer_reason")
    def _check_key_transfer_reason(self):
        for rec in self:
            duplicate = self.config_id.typology_ids.filtered(
                lambda x: x.id != rec.id
                and x.key == rec.key
                and x.transfer_reason == rec.transfer_reason
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "Key and Transfer Reason must be unique in the same configuration."
                    )
                )
