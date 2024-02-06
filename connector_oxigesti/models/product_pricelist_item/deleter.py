# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OxigestiExportDeleter(Component):
    """Base Export Deleter for Oxigesti"""

    _name = "oxigesti.product.pricelist.item.export.deleter"
    _inherit = "oxigesti.export.deleter"

    _apply_on = "oxigesti.product.pricelist.item"

    def run(self, external_id):
        adapter = self.component(usage="backend.adapter")
        adapter.write(external_id, {"deprecated": True})


class OxigestiDelayedBatchExportDeleter(Component):
    _name = "oxigesti.product.pricelist.item.delayed.batch.export.deleter"
    _inherit = "oxigesti.delayed.batch.export.deleter"

    _apply_on = "oxigesti.product.pricelist.item"
