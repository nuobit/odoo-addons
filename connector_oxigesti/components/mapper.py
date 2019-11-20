# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping


class OxigestiImportMapper(AbstractComponent):
    _name = 'oxigesti.import.mapper'
    _inherit = ['base.import.mapper', 'base.oxigesti.connector']


class OxigestiImportMapChild(AbstractComponent):
    _name = 'oxigesti.map.child.import'
    _inherit = ['base.map.child.import', 'base.oxigesti.connector']
