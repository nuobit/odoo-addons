# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BarcodeLabelTemplateConfiguration(models.Model):
    _name = "barcode.label.template.configuration"
    _order = "default desc"

    name = fields.Char(required=True)
    template = fields.Binary()
    template_name = fields.Char()
    paperformat_id = fields.Many2one(comodel_name="report.paperformat", required=True)
    default = fields.Boolean()
    position_x = fields.Float()
    position_y = fields.Float()
    width = fields.Float()

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                config = self.search([("id", "!=", rec.id), ("default", "=", True)])
                if config:
                    raise ValidationError(_("There is already a default configuration"))
