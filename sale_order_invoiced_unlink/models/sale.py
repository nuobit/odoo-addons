# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def unlink(self):
        if self.mapped("order_line.invoice_lines"):
            raise UserError(
                _(
                    "You can not remove sales order if it has lines "
                    "linked to any invoice line."
                )
            )
        return super(SaleOrder, self).unlink()
