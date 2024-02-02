# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class OxigestiExportDeleter(AbstractComponent):
    """Base Export Deleter for Oxigesti"""

    _name = "oxigesti.export.deleter"
    _inherit = ["base.deleter", "base.oxigesti.connector"]

    _usage = "record.export.deleter"

    def run(self, external_id):
        adapter = self.component(usage="backend.adapter")
        adapter.delete(external_id)
