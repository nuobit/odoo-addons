# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseSapB1Connector(AbstractComponent):
    _name = "base.sapb1.connector"
    _inherit = "base.connector"
    _collection = "sapb1.backend"

    _description = "Base SAP B1 Connector Component"
