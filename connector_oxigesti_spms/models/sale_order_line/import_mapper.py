# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class OxigestiSpmsSaleOrderLineImporterMapper(Component):
    _name = "oxigesti.spms.sale.order.line.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.sale.order.line"
    _usage = "import.mapper"

    direct = [
        ("NumeroPrescricao", "spms_prescription"),
        ("NumeroUtente", "spms_user_number"),
        ("NumeroBenef", "spms_beneficiary_number"),
        ("DataInicio", "spms_start_date"),
        ("DataFim", "spms_end_date"),
        # ("CodigoMotivoSuspensao", "spms_suspension_reason_code"),
        # ("CodigoContexto", "spms_context_code"),
        # ("CodigoPrescricao", "spms_prescription_type_code"),
        ("LinhaDispensa_Quantidade", "product_uom_qty"),
    ]

    @changed_by("product_id")
    @mapping
    def product(self, record):
        binder = self.binder_for("oxigesti.spms.product.product")
        external_id = record["LinhaDispensa_Sistema"]
        product = binder.to_internal(external_id, unwrap=True)
        assert product, (
            "product_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"product_id": product.id}

    @changed_by("spms_suspension_reason_id")
    @mapping
    def smpms_suspension_reason_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.suspension.reason")
        external_id = record["MotivoSuspensao"]
        if not external_id:
            return {"spms_suspension_reason_id": None}
        suspension_reason = binder.to_internal(external_id, unwrap=True)
        assert suspension_reason, (
            "spms_suspension_reason_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"spms_suspension_reason_id": suspension_reason.id}

    @changed_by("spms_prescription_type_id")
    @mapping
    def spms_prescription_type_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.prescription.type")
        external_id = record["TipoPrescricao"]
        prescription_type = binder.to_internal(external_id, unwrap=True)
        assert prescription_type, (
            "spms_prescription_type_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"spms_prescription_type_id": prescription_type.id}

    @changed_by("spms_suspension_reason_id")
    @mapping
    def spms_context_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.context")
        external_id = record["LinhaDispensa_Contexto"]
        context = binder.to_internal(external_id, unwrap=True)
        assert context, (
            "spms_context_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"spms_context_id": context.id}
