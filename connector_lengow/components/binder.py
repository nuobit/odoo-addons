# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class LengowBinder(AbstractComponent):
    _name = "lengow.binder"
    _inherit = ['base.binder.composite', 'base.lengow.connector']
