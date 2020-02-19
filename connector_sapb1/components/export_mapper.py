# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping


class SAPB1ExportMapper(AbstractComponent):
    _name = 'sapb1.export.mapper'
    _inherit = ['base.export.mapper', 'base.sapb1.connector']


class SAPB1ExportMapChild(AbstractComponent):
    _name = 'sapb1.map.child.export'
    _inherit = ['base.map.child.export', 'base.sapb1.connector']
