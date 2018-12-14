# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseAmbugestConnectorComponent(AbstractComponent):
    """ Base Ambugest Connector Component

    All components of this connector should inherit from it.
    """

    _name = 'base.ambugest.connector'
    _inherit = 'base.connector'
    _collection = 'ambugest.backend'
