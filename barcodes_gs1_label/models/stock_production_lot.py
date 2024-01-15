# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def print_gs1_barcode_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "barcodes_gs1_label.barcodes_lot_option_wizard_view_action"
        )
        return action

    gs1_generated = fields.Boolean()

    @api.onchange("gs1_generated")
    def _onchange_gs1_generated(self):
        if not self.gs1_generated and self._origin.id:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("A GS1 code has been generated with this data."),
                },
            }

    @api.constrains("name", "ref")
    def _check_name(self):
        for rec in self:
            if rec.gs1_generated:
                raise ValidationError(
                    _(
                        "If the lot has a GS1 generated, the Lot/Serial "
                        "Number and Internal Reference cannot be modified"
                    )
                )
