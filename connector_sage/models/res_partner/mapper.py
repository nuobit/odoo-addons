# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ResPartnerImportMapper(Component):
    _name = "sage.partner.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.res.partner"

    direct = [
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("CodigoEmpleado", "sage_codigo_empleado"),
        # (normalize_datetime('created_at'), 'created_at'),
        # (normalize_datetime('updated_at'), 'updated_at'),
        # ('email', 'emailid'),
        # ('Dni', 'vat'),
    ]

    @only_create
    @mapping
    def email(self, record):
        return {"email": record["Email1"] or False}

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def email2_comment(self, record):
        if record["Email1"] != record["Email2"]:
            return {"comment": record["Email2"]}

    @only_create
    @mapping
    def is_company(self, record):
        return {"is_company": False}

    @only_create
    @mapping
    def company_type(self, record):
        return {"company_type": "person"}

    @only_create
    @mapping
    def names(self, record):
        parts = [
            part
            for part in (
                record["NombreEmpleado"],
                record["PrimerApellidoEmpleado"],
                record["SegundoApellidoEmpleado"],
            )
            if part
        ]
        return {"name": " ".join(parts)}

    @only_create
    @mapping
    def ref(self, record):
        return {"ref": str(record["CodigoEmpleado"])}

    @only_create
    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    # @only_create
    # @mapping
    # def customer(self, record):
    #     return {"customer_rank": 0}
    #
    # @mapping
    # def employee_as_supplier(self, record):
    #     return {"supplier_rank": 1}

    @only_create
    @mapping
    def employee_as_supplier_account(self, record):
        return {
            "property_account_payable_id": (
                self.backend_record.import_employees_default_account_payable_id.id
            )
        }

    @only_create
    @mapping
    def type(self, record):
        return {"type": "contact"}

    def sage_identity(self, record):
        """Normalize a Sage person identity (SiglaNacion+Dni) to a string.

        Single source of the normalization: euvat seeds the partner vat
        with it and the reassignment guard compares against that vat, so
        both sides must build the string exactly the same way.
        """
        parts = [part for part in (record["SiglaNacion"], record["Dni"]) if part]
        return "".join(parts).strip().upper()

    @only_create
    @mapping
    def euvat(self, record):
        nif_pattern = self.backend_record.employees_exclude_nif_pattern
        if nif_pattern:
            m = re.match(nif_pattern, record["Dni"])
            if m:
                return {"vat": None}
        return {"vat": self.sage_identity(record)}
