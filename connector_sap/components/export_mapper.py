# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SapExportMapper(AbstractComponent):
    _name = 'sap.export.mapper'
    _inherit = ['base.export.mapper', 'base.sap.connector']


class SapExportMapChild(AbstractComponent):
    _name = 'sap.map.child.export'
    _inherit = ['base.map.child.export', 'base.sap.connector']
