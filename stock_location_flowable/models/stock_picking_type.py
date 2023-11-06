# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    flowable_operation = fields.Boolean(copy=False)

    @api.constrains("flowable_operation", "code", "warehouse_id", "company_id")
    def _check_flowable_operation(self):
        for rec in self:
            if rec.flowable_operation:
                if rec.code != "mrp_operation":
                    raise ValidationError(
                        _("Only manufacturing picking types can be flowable."),
                    )
                if (
                    rec.env["stock.picking.type"].search_count(
                        [
                            ("flowable_operation", "=", True),
                            ("warehouse_id", "=", rec.warehouse_id.id),
                            ("code", "=", rec.code),
                            ("company_id", "=", rec.company_id.id),
                        ]
                    )
                    > 1
                ):
                    raise ValidationError(
                        _("Only one picking type can be flowable in a warehouse %s.")
                        % rec.warehouse_id.name,
                    )
