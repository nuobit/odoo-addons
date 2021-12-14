# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductListener(Component):
    _name = "oxigesti.product.product.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.product"
