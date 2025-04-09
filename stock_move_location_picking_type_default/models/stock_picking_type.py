# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_in_location_moves = fields.Boolean()

    @api.constrains("use_in_location_moves", "code")
    def _check_use_in_location_moves_code(self):
        for rec in self:
            if rec.use_in_location_moves and rec.code != "internal":
                raise ValidationError(
                    _(
                        "Field 'Use in location moves' can only be activated for "
                        "'Internal Transfer' operations."
                    )
                )

    @api.constrains("use_in_location_moves", "company_id")
    def _check_unique_use_in_location_moves_per_company(self):
        for rec in self:
            if rec.use_in_location_moves:
                existing = self.search(
                    [
                        ("use_in_location_moves", "=", True),
                        ("company_id", "=", rec.company_id.id),
                        ("id", "!=", rec.id),
                    ]
                )
                if existing:
                    raise ValidationError(
                        _(
                            "Only one operation type can be marked with 'Use in "
                            "location moves' per company. Please uncheck '%s' before "
                            "continuing."
                        )
                        % (existing.display_name)
                    )
