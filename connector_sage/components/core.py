# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SageBaseConnectorComponent(AbstractComponent):
    """Base Sage Connector Component

    All components of this connector should inherit from it.
    """

    _name = "base.sage.connector"
    _inherit = "base.connector"
    _collection = "sage.backend"
