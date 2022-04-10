# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductBinder(Component):
    _name = 'sap.product.product.binder'
    _inherit = 'sap.binder'

    _apply_on = 'sap.product.product'

    _external_field = 'ItemCode'
    _internal_field = 'sap_sku'
    # _internal_alt_field = "sap_sku"
    _external_alt_field = "ItemCode"
