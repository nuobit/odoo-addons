# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def unlink(self):
        res = super().unlink()
        for rec in self:
            item = (
                self.env["product.pricelist.item"]
                .search(
                    [
                        ("product_tmpl_id", "=", rec.id),
                        ("oxigesti_bind_ids", "!=", False),
                    ]
                )
                .filtered(lambda x: not all(x.oxigesti_bind_ids.mapped("deprecated")))
            )
            if item:
                item.unlink()
        return res
