# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo import tools


class LightingProductBinder(Component):
    """ Bind records and give odoo/sapbb1 ids correspondence

    Binding models are models called ``sapb1.{normal_model}``,
    like ``sapb1.lighting.product``.
    They are ``_inherits`` of the normal models and contains
    the SAP B1 ID, the ID of the SAP B1 Backend and the additional
    fields belonging to the SAP B1 instance.
    """
    _name = 'sapb1.lighting.product.binder'
    _inherit = 'sapb1.binder'

    _apply_on = 'sapb1.lighting.product'
