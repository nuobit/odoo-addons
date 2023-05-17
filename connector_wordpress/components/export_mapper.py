# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WordPressExportMapper(AbstractComponent):
    _name = "wordpress.export.mapper"
    _inherit = ["connector.extension.export.mapper", "base.wordpress.connector"]
