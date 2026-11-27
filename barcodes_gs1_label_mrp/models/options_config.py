# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models


class BarcodesGS1LabelOptionsConfig(models.Model):
    _inherit = "barcodes.gs1.label.options.config"

    @api.model
    def _move_state_selection(self):
        return self.env["stock.move"]._fields["state"].args["selection"]

    allow_print_states = fields.Selection(
        selection=_move_state_selection,
        string="Allow print states",
        default="done",
    )
