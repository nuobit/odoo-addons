# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class AmbugestImportMapper(AbstractComponent):
    _name = "ambugest.import.mapper"
    _inherit = ["base.import.mapper", "base.ambugest.connector"]


class AmbugestImportMapChild(AbstractComponent):
    _name = "ambugest.map.child.import"
    _inherit = ["base.map.child.import", "base.ambugest.connector"]
