# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def get_splited_line_component_description(self):
        return self.product_id.display_name
