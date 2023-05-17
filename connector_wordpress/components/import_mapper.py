# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WordPressImportMapper(AbstractComponent):
    _name = "wordpress.import.mapper"
    _inherit = ["base.import.mapper", "base.wordpress.connector"]
