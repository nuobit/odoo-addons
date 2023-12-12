# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductImportMapper(Component):
    _name = "lengow.product.product.import.mapper"
    _inherit = "lengow.import.mapper"

    _apply_on = "lengow.product.product"

    direct = [("sku", "default_code")]
