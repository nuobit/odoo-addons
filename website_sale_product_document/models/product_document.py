# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductDocument(models.AbstractModel):
    _inherit = "product.document"

    datas_fname = fields.Char(string="Filename")
