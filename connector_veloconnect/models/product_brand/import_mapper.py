# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductBrandImportMapper(Component):
    _name = "veloconnect.product.brand.import.mapper"
    _inherit = "veloconnect.import.mapper"

    _apply_on = "veloconnect.product.brand"

    direct = [
        ("ManufacturersItemIdentificationName", "name"),
    ]
