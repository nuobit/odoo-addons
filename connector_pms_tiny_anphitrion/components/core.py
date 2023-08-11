# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseAnphitrionConnector(AbstractComponent):
    _name = "base.anphitrion.connector"
    _inherit = "base.connector"
    _collection = "anphitrion.backend"

    _description = "Base Anphitrion Connector Component"
