# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SAPB1BaseConnectorComponent(AbstractComponent):
    """ Base SAP B1 Connector Component

    All components of this connector should inherit from it.
    """

    _name = 'base.sapb1.connector'
    _inherit = 'base.connector'
    _collection = 'sapb1.backend'
