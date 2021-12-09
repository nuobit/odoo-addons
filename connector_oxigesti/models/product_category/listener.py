# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductCategoryListener(Component):
    _name = "oxigesti.product.category.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.category"
