# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def action_done(self):
        for line in self.mapped('line_ids'):
            if line.product_id.tracking != 'none' and not line.prod_lot_id:
                if line.product_qty != 0:
                    raise UserError(
                        _("The product (%s) has tracking defined (%s), "
                          "therefore it's necessary to enter the corresponding tracking number.") %
                        (line.product_id.display_name, line.product_id.tracking))
            elif line.product_id.tracking == 'none' and line.prod_lot_id:
                if line.product_qty != 0:
                    raise UserError(
                        _("The product (%s) has no tracking defined, "
                          "therefore you don't need to enter any tracking number.") %
                        line.product_id.display_name)

        res = super(Inventory, self).action_done()

        return res
