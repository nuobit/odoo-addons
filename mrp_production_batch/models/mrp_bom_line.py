# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    use_in_batch = fields.Boolean()

    @api.constrains("use_in_batch")
    def _check_use_in_batch(self):
        for rec in self:
            if len(rec.bom_id.bom_line_ids.filtered(lambda x: x.use_in_batch)) > 1:
                raise ValidationError(
                    _("You can't set more than one component to be used in a batch.")
                )
