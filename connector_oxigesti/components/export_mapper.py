# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping


class OxigestiExportMapper(AbstractComponent):
    _name = 'oxigesti.export.mapper'
    _inherit = ['base.export.mapper', 'base.oxigesti.connector']


class OxigestiExportMapChild(AbstractComponent):
    _name = 'oxigesti.map.child.export'
    _inherit = ['base.map.child.export', 'base.oxigesti.connector']
