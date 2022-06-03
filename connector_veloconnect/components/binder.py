# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class VeloconnectBinder(AbstractComponent):
    _name = "veloconnect.binder"
    _inherit = ['base.binder.composite', 'base.veloconnect.connector']
