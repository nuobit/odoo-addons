# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductBinder(Component):
    _name = "lengow.product.product.binder"
    _inherit = "lengow.binder"

    _apply_on = "lengow.product.product"

    external_id = "sku"
    internal_id = "lengow_sku"
    internal_alt_id = "default_code"
