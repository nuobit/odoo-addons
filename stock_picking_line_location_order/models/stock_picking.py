# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

BIG_STRING = "\xff\xff\xff"


class Picking(models.Model):
    _inherit = "stock.picking"

    def _get_move_ids_without_package(self):
        def get_move_key(move):
            move_lines = move.move_line_ids.location_sorted()
            return (
                move_lines and move_lines[0].location_id.name or BIG_STRING,
                move.product_id.default_code or BIG_STRING,
                move.product_id.id,
            )

        return super()._get_move_ids_without_package().sorted(get_move_key)
