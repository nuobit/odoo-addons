# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SageImportMapper(AbstractComponent):
    _name = "sage.import.mapper"
    _inherit = ["base.import.mapper", "base.sage.connector"]
