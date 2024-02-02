# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def unlink(self):
        for rec in self:
            for item in rec.item_ids.filtered(lambda x: x.oxigesti_bind_ids):
                item.unlink()
        return super().unlink()
