# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    is_regularization = fields.Boolean(copy=False)

    @api.constrains("is_regularization", "code", "warehouse_id", "company_id")
    def _check_is_regularization(self):
        for rec in self:
            if rec.is_regularization:
                if rec.code != "internal":
                    raise ValidationError(
                        _("Only internal picking types can be regularization."),
                    )
                if (
                    rec.env["stock.picking.type"].search_count(
                        [
                            ("is_regularization", "=", True),
                            ("warehouse_id", "=", rec.warehouse_id.id),
                            ("code", "=", rec.code),
                            ("company_id", "=", rec.company_id.id),
                        ]
                    )
                    > 1
                ):
                    raise ValidationError(
                        _(
                            "Only one picking type can be regularization in a warehouse %s."
                        )
                        % rec.warehouse_id.name,
                    )
