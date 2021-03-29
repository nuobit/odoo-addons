# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("default_code", "company_id")
    def _check_default_code(self):
        for record in self:
            products = (
                self.env["product.product"]
                .sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("product_tmpl_id", "=", record.id),
                        ("default_code", "!=", False),
                    ]
                )
            )
            for product in products:
                product._check_default_code(record.default_code)
