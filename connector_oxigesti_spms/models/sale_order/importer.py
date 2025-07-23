# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderBatchDirectImporter(Component):
    _name = "oxigesti.spms.sale.order.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.sale.order"


class OxigestiSPMSSaleOrderBatchDelayedImporter(Component):
    _name = "oxigesti.spms.sale.order.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.sale.order"


class OxigestiSPMSSaleOrderRecordDirectImporter(Component):
    _name = "oxigesti.spms.sale.order.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.sale.order"

    def _import_dependencies(self, external_data, sync_date):
        external_partner_id = external_data["UnidadeLocalSalude"]
        self._import_dependency(
            external_partner_id, "oxigesti.spms.res.partner", sync_date
        )

        for external_product_id in {
            x["LinhaDispensa_Sistema"] for x in external_data["lines"]
        }:
            self._import_dependency(
                external_product_id, "oxigesti.spms.product.product", sync_date
            )

        # SPMS Suspension Reasons
        for external_suspension_reason_id in {
            x["MotivoSuspensao"] for x in external_data["lines"]
        }:
            self._import_dependency(
                external_suspension_reason_id,
                "oxigesti.spms.spms.suspension.reason",
                sync_date,
            )

        # SPMS Prescription Types
        for external_prescription_type_id in {
            x["TipoPrescricao"] for x in external_data["lines"]
        }:
            self._import_dependency(
                external_prescription_type_id,
                "oxigesti.spms.spms.prescription.type",
                sync_date,
            )

        # SPMS Context
        for external_context_id in {
            x["LinhaDispensa_Contexto"] for x in external_data["lines"]
        }:
            self._import_dependency(
                external_context_id, "oxigesti.spms.spms.context", sync_date
            )

    def _after_import(self, binding):
        # order validation
        binder = self.component(usage="binder")
        sale_order = binder.unwrap_binding(binding)
        sale_order.onchange_partner_id()
        for line in sale_order.order_line:
            line.product_id_change()
        sale_order.with_context(skip_reserved_quantity=True).action_confirm()

    # TODO: import sale order locked error
    # if sale_order.state == "sale":
    #     sale_order.action_done()
