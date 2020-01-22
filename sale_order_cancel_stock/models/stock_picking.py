# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_cancel(self):
        if not self.env.context.get('from_order'):
            return super(StockPicking, self).action_cancel()

        qty_balances = {}
        moves_lines_done = self.mapped('move_lines') \
            .filtered(lambda x: x.state == 'done').mapped('move_line_ids')
        for line in moves_lines_done:
            if line.qty_done:
                lot_id = not line.lot_id and None or line.lot_id.id
                key = (line.product_id.id, lot_id)

                qty_balances.setdefault(line.location_id.id, {}) \
                    .setdefault(key, 0)
                qty_balances[line.location_id.id][key] -= line.qty_done
                if not qty_balances[line.location_id.id][key]:
                    del qty_balances[line.location_id.id][key]

                qty_balances.setdefault(line.location_dest_id.id, {}) \
                    .setdefault(key, 0)
                qty_balances[line.location_dest_id.id][key] += line.qty_done
                if not qty_balances[line.location_dest_id.id][key]:
                    del qty_balances[line.location_dest_id.id][key]

                if not qty_balances[line.location_id.id]:
                    del qty_balances[line.location_id.id]
                if not qty_balances[line.location_dest_id.id]:
                    del qty_balances[line.location_dest_id.id]

        if qty_balances:
            return super(StockPicking, self).action_cancel()

        self.mapped('move_lines') \
            .filtered(lambda x: x.state != 'done')._action_cancel()

        self.write({'is_locked': True})

        return True
