# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SapImportMapper(AbstractComponent):
    _name = 'sap.import.mapper'
    _inherit = ['base.import.mapper', 'base.sap.connector']


class SapImportMapChild(AbstractComponent):
    _name = 'sap.map.child.import'
    _inherit = ['base.map.child.import', 'base.sap.connector']
