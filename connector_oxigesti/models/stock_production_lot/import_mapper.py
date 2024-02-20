# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ResPartnerImportMapper(Component):
    _name = "oxigesti.stock.production.lot.import.mapper"
    _inherit = "oxigesti.import.mapper"

    _apply_on = "oxigesti.stock.production.lot"

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    # This is not needed as we don't allow creating new lots
    # (buy we do allow creating new bindings to link existing lots)
    # @only_create
    # @mapping
    # def name(self, record):
    #     return {"name": record["Lote"]}
    #
    # @only_create
    # @mapping
    # def product_id(self, record):
    #     oxigesti_articulo = record["CodigoArticulo"]
    #     binding = (
    #         self.env["oxigesti.product.product"]
    #         .with_context(active_test=False)
    #         .search(
    #             [
    #                 ("company_id", "=", self.backend_record.company_id.id),
    #                 ("default_code", "=", oxigesti_articulo),
    #             ]
    #         )
    #     )
    #     if not binding:
    #         raise AssertionError(
    #             "Product %s should have been exported in "
    #             "StockProductionLotImporter._import_dependencies" % (oxigesti_articulo,)
    #         )
    #     if len(binding) > 1:
    #         raise AssertionError(
    #             "Found more than 1 products (%i) with "
    #             "the same code (%s) in Odoo: %s"
    #             % (len(binding), oxigesti_articulo, binding.mapped("odoo_id.id"))
    #         )
    #     product = self.binder_for().unwrap_binding(binding)
    #     return {"product_id": product.id}

    @mapping
    def nos(self, record):
        values = {}
        if not record["nos_unknown"]:
            values["nos"] = record["nos"]
        # we cannot put the "nos_unknown" at the beginning of the dictionary
        # in 'values' variable because the order matters otherwise
        # Odoo will throw a constraint of the module oxigen_stock_alternate_lot
        values["nos_unknown"] = record["nos_unknown"]
        return values

    @mapping
    def dn(self, record):
        values = {}
        if not record["dn_unknown"]:
            values["dn"] = record["dn"]
        # we cannot put the "dn_unknown" at the beginning of the dictionary
        # in 'values' variable because the order matters otherwise
        # Odoo will throw a constraint of the module oxigen_stock_alternate_lot
        values["dn_unknown"] = record["dn_unknown"]
        return values

    @mapping
    def oxigesti_write_date(self, record):
        return {"oxigesti_write_date": record["write_date"]}

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the record on a existing stock_production_lot
        with the same internal references"""
        codigoarticulo = record["CodigoArticulo"]
        lote = record["Lote"]
        if codigoarticulo and lote:
            product = self.env["product.product"].search(
                [
                    ("company_id", "=", self.backend_record.company_id.id),
                    ("default_code", "=", codigoarticulo),
                ]
            )
            if not product:
                return
            stock_production_lot = (
                self.env["stock.production.lot"]
                .with_context(active_test=False)
                .search(
                    [
                        ("company_id", "=", self.backend_record.company_id.id),
                        ("name", "=", lote),
                        ("product_id", "=", product.id),
                    ]
                )
            )
            if stock_production_lot:
                # check if exists another binding with the same reference
                other_binding = self.model.with_context(active_test=False).search(
                    [
                        ("backend_id", "=", self.backend_record.id),
                        ("odoo_id", "=", stock_production_lot.id),
                    ]
                )
                if other_binding:
                    raise Exception(
                        _(
                            "Already exists a binding with the Lot: '%s' "
                            "but with another external id: '%s'.\n"
                            "This could be caused by "
                            "a duplicated external reference on the backend"
                        )
                        % (stock_production_lot.name, other_binding.external_id_display)
                    )
                return {"odoo_id": stock_production_lot.id}
