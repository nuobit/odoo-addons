# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from ..common import tools


class ProductBrand(models.Model):
    _inherit = "product.brand"

    name_slug = fields.Char(
        string="Slug", compute="_compute_name_slug", search="_search_name_slug"
    )

    def _compute_name_slug(self):
        for rec in self:
            rec.name_slug = tools.slugify(rec.name)

    def _search_name_slug(self, operator, value):
        if operator != "=":
            raise ValueError("Operator not supported")
        brands = (
            self.env[self._name].search([]).filtered(lambda x: x.name_slug == value)
        )
        return [("id", "in", brands.ids)]
