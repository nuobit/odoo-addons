# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderGenericRecordDirectExportDeleter(Component):

    _name = "oxigesti.spms.sale.order.record.direct.export.deleter"
    _inherit = "oxigesti.spms.generic.record.direct.export.deleter"

    def _delete(self, external_id, binding):
        return self.backend_adapter.write(
            external_id,
            {
                "Odoo_Numero_Albaran": None,
                "Odoo_Fecha_Generado_Albaran": None,
            },
        )
