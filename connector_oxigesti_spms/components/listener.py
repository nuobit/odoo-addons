# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OXigestiSPMSListener(AbstractComponent):
    _name = "oxigesti.spms.listener"
    _inherit = ["connector.extension.event.listener", "oxigesti.spms.connector"]
