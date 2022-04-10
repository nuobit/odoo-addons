# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class SapB1Binder(AbstractComponent):
    _name = "sapb1.binder"
    _inherit = ['base.binder.composite', 'base.sapb1.connector']

    _binding_field = 'sapb1_bind_ids'
