# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class AmbugestModelBinder(AbstractComponent):
    """Bind records and give odoo/ambugest ids correspondence

    Binding models are models called ``ambugest.{normal_model}``,
    like ``ambugest.res.partner`` or ``ambugest.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Ambugest ID, the ID of the Ambugest Backend and the additional
    fields belonging to the Ambugest instance.
    """

    _name = "ambugest.binder"
    _inherit = ["base.binder.composite", "base.ambugest.connector"]
