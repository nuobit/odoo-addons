# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def get_delivery_note_moves(self):
        moves_by_product = {}
        for move in self.move_lines:
            if move.bom_line_id and move.bom_line_id.bom_id.type == "phantom":
                if move.sale_line_id:
                    product = move.sale_line_id.product_id
                else:
                    bom = move.bom_line_id.bom_id
                    product = bom.product_id or bom.product_tmpl_id
            else:
                product = False
            moves_by_product.setdefault(product, self.env["stock.move"])
            moves_by_product[product] |= move
        return list(moves_by_product.items())
