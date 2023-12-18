# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SapB1ExportMapper(AbstractComponent):
    _name = "sapb1.export.mapper"
    _inherit = ["connector.extension.export.mapper", "base.sapb1.connector"]


class SapB1ExportMapChild(AbstractComponent):
    _name = "sapb1.map.child.export"
    _inherit = ["connector.extension.map.child.export", "base.sapb1.connector"]
