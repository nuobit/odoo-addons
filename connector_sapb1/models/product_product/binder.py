# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductBinder(Component):
    _name = "sapb1.product.product.binder"
    _inherit = "sapb1.binder"

    _apply_on = "sapb1.product.product"

    _external_field = "ItemCode"
    _internal_field = "sapb1_sku"
    _external_alt_field = "ItemCode"
