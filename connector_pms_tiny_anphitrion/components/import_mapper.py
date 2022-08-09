# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class AnphitrionImportMapper(AbstractComponent):
    _name = "anphitrion.import.mapper"
    _inherit = ["base.import.mapper", "base.anphitrion.connector"]


class AnphitrionImportMapChild(AbstractComponent):
    _name = "anphitrion.map.child.import"
    _inherit = ["base.map.child.import", "base.anphitrion.connector"]
