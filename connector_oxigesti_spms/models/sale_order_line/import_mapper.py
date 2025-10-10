# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


class OxigestiSpmsSaleOrderLineImporterMapper(Component):
    _name = "oxigesti.spms.sale.order.line.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.sale.order.line"
    _usage = "import.mapper"

    @only_create
    @mapping
    def spms_prescription(self, record):
        return {"spms_prescription": record["NumeroPrescricao"]}

    @only_create
    @mapping
    def spms_user_number(self, record):
        return {"spms_user_number": record["NumeroUtente"]}

    @only_create
    @mapping
    def spms_beneficiary_number(self, record):
        return {"spms_beneficiary_number": record["NumeroBenef"]}

    @only_create
    @mapping
    def spms_start_date(self, record):
        return {"spms_start_date": record["DataInicio"]}

    @only_create
    @mapping
    def spms_end_date(self, record):
        return {"spms_end_date": record["DataFim"]}

    @changed_by("product_id")
    @mapping
    def product(self, record):
        binder = self.binder_for("oxigesti.spms.product.product")
        external_id = record["LinhaDispensa_Sistema"]
        product = binder.to_internal(external_id, unwrap=True)
        assert product, (
            f"product_id {external_id} should have been imported in "
            f"SaleOrderImporter._import_dependencies"
        )
        # TODO: Move this to upper class
        binding = self.options["binding"]
        if binding and binding.product_id == product:
            return
        return {"product_id": product.id}

    @changed_by("product_uom_qty")
    @mapping
    def product_uom_qty(self, record):
        binding = self.options["binding"]
        if binding and binding.product_uom_qty == record["LinhaDispensa_Quantidade"]:
            return
        return {"product_uom_qty": record["LinhaDispensa_Quantidade"]}

    @changed_by("spms_suspension_reason_id")
    @mapping
    def smpms_suspension_reason_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.suspension.reason")
        external_id = record["MotivoSuspensao"]
        if not external_id:
            return {"spms_suspension_reason_id": None}
        suspension_reason = binder.to_internal(external_id, unwrap=True)
        assert suspension_reason, (
            f"spms_suspension_reason_id {external_id} should have been imported in "
            f"SaleOrderImporter._import_dependencies"
        )
        return {"spms_suspension_reason_id": suspension_reason.id}

    @changed_by("spms_prescription_type_id")
    @mapping
    def spms_prescription_type_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.prescription.type")
        external_id = record["TipoPrescricao"]
        prescription_type = binder.to_internal(external_id, unwrap=True)
        assert prescription_type, (
            f"spms_prescription_type_id {external_id} should have been imported in "
            f"SaleOrderImporter._import_dependencies"
        )
        return {"spms_prescription_type_id": prescription_type.id}

    @changed_by("spms_suspension_reason_id")
    @mapping
    def spms_context_code(self, record):
        binder = self.binder_for("oxigesti.spms.spms.context")
        external_id = record["LinhaDispensa_Contexto"]
        context = binder.to_internal(external_id, unwrap=True)
        assert context, (
            f"spms_context_id {external_id} should have been imported in "
            f"SaleOrderImporter._import_dependencies"
        )
        return {"spms_context_id": context.id}

    # def _get_protected_fields(self):
    #     return [
    #         'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty',
    #         'tax_id', 'analytic_tag_ids'
    #     ]
