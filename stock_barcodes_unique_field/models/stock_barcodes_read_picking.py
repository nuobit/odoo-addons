# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def action_confirm(self):
        res = super().action_confirm()
        option_fields = self.option_group_id.option_ids.filtered(lambda x: x.unique)
        for option in option_fields:
            field = option.field_name
            move_line_field = self.move_line_ids[field]
            if len(move_line_field) > 1:
                field_label = self.fields_get([field])[field]["string"]
                raise UserError(
                    _(
                        "The field %s must have the same value in all the "
                        "lines of the picking because you have selected it as "
                        "a static field in the barcode options."
                    )
                    % field_label
                )
            if move_line_field and option.copy_to_header:
                if (
                    field in self.picking_id
                    and move_line_field != self.picking_id[field]
                ):
                    self.picking_id[field] = move_line_field
        return res
