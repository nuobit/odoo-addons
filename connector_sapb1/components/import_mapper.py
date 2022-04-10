# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SapB1ImportMapper(AbstractComponent):
    _name = 'sapb1.import.mapper'
    _inherit = ['base.import.mapper', 'base.sapb1.connector']


class SapB1ImportMapChild(AbstractComponent):
    _name = 'sapb1.map.child.import'
    _inherit = ['base.map.child.import', 'base.sapb1.connector']
