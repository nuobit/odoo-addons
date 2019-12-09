# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo import tools


class ProductBuyerinfoBinder(Component):
    _name = 'oxigesti.product.buyerinfo.binder'
    _inherit = 'oxigesti.binder'
    _apply_on = 'oxigesti.product.buyerinfo'
