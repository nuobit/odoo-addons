# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class VeloconnectImportMapper(AbstractComponent):
    _name = "veloconnect.import.mapper"
    _inherit = ["base.import.mapper", "base.veloconnect.connector"]


class VeloconnectImportMapChild(AbstractComponent):
    _name = "veloconnect.map.child.import"
    _inherit = ["base.map.child.import", "base.veloconnect.connector"]
