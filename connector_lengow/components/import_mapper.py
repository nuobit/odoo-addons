# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class LengowImportMapper(AbstractComponent):
    _name = "lengow.import.mapper"
    _inherit = ["base.import.mapper", "base.lengow.connector"]


class LengowImportMapChild(AbstractComponent):
    _name = "lengow.map.child.import"
    _inherit = ["base.map.child.import", "base.lengow.connector"]
