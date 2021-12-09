# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductProductImportMapper(Component):
    _name = "ambugest.product.product.import.mapper"
    _inherit = "ambugest.import.mapper"
    _apply_on = "ambugest.product.product"

    direct = [
        ("Id", "ambugest_id"),
        ("Empresa", "ambugest_empresa"),
    ]

    @mapping
    def purchase_ok(self, record):
        return {"purchase_ok": False}

    @mapping
    def product_type(self, record):
        return {"type": "service", "invoice_policy": "order"}

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    @only_create
    @mapping
    def default_code(self, record):
        return {"default_code": record["Odoo_Articulo"]}

    @only_create
    @mapping
    def name(self, record):
        return {"name": record["Articulo"].strip()}

    @only_create
    @mapping
    def taxes(self, record):
        tax_ref = "%s.%i_%s" % (
            "l10n_es",
            self.backend_record.company_id.id,
            "account_tax_template_s_iva0",
        )
        tax_id = self.env.ref(tax_ref).id

        return {
            "taxes_id": [(6, False, [tax_id])],
            "supplier_taxes_id": [(6, False, [])],
        }

    @only_create
    @mapping
    def uom(self, record):
        uom_map = {
            "Traslado": "uom.product_uom_unit",
            "Kms": "uom.product_uom_km",
            "Horas_Medico_4ph": "uom.product_uom_hour",
            "Horas_DUE_4ph": "uom.product_uom_hour",
            "Horas_Espera": "uom.product_uom_hour",
        }

        for ambugest_uom, odoo_uom_ext_id in uom_map.items():
            if record[ambugest_uom]:
                return {
                    "uom_id": self.env.ref(odoo_uom_ext_id).id,
                    "uom_po_id": self.env.ref(odoo_uom_ext_id).id,
                }

        return {
            "uom_id": self.env.ref("uom.product_uom_unit").id,
            "uom_po_id": self.env.ref("uom.product_uom_unit").id,
        }

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the product on a existing product
        with the same internal reference"""
        product = self.env["product.product"].search(
            [
                ("company_id", "=", self.backend_record.company_id.id),
                ("default_code", "=", record["Odoo_Articulo"]),
            ]
        )
        if product:
            if len(product) > 1:
                raise Exception(
                    "There's more than one existing products "
                    "with the same Internal reference %s" % record["Odoo_Articulo"]
                )
            return {"odoo_id": (product.id, False, None)}
