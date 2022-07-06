# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductSupplierinfoBinder(Component):
    _name = 'veloconnect.product.supplierinfo.binder'
    _inherit = 'veloconnect.binder'
#
    _apply_on = 'product.supplierinfo'
#
#     _external_field = ['SellersItemIdentificationID', 'MinimumQuantity']
    _internal_field = ['name.id', 'product_code', 'min_qty']
#
#     _internal_alt_field = ['name', 'product_code', 'min_qty']
