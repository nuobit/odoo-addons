# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockBarcodesOption(models.Model):
    _inherit = "stock.barcodes.option"

    unique = fields.Boolean()
    copy_to_header = fields.Boolean()

    @api.constrains("unique", "copy_to_header")
    def _check_copy_to_header(self):
        for rec in self:
            if not rec.unique and rec.copy_to_header:
                raise ValidationError(
                    _(
                        "The field 'Copy to Header' can only be checked if the "
                        "field 'Unique' is also checked."
                    )
                )
