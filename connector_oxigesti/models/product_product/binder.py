# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo import tools


class ProductProductBinder(Component):
    """ Bind records and give odoo/oxigesti ids correspondence

    Binding models are models called ``oxigesti.{normal_model}``,
    like ``oxigesti.res.partner`` or ``oxigesti.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Oxigesti ID, the ID of the Oxigesti Backend and the additional
    fields belonging to the Oxigesti instance.
    """
    _name = 'oxigesti.product.product.binder'
    _inherit = 'oxigesti.binder'

    _apply_on = 'oxigesti.product.product'
