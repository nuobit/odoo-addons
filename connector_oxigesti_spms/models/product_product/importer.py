# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSProductProductBatchDirectImporter(Component):
    _name = "oxigesti.spms.product.product.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.product.product"


class OxigestiSPMSProductProductBatchDelayedImporter(Component):
    _name = "oxigesti.spms.product.product.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.product.product"


class OxigestiSPMSProductProductBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.product.product.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.product.product"

    def _import_dependencies(self, external_data, sync_date, external_fields=None):
        external_partner_id = external_data["Lote"]
        self._import_dependency(
            external_partner_id, "oxigesti.spms.spms.lot", sync_date
        )
