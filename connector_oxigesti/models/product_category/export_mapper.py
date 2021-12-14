# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class ProductBuyerExportMapper(Component):
    _name = "oxigesti.product.category.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.product.category"

    @changed_by("odoo_id")
    @mapping
    def IdCategoriaOdoo(self, record):
        return {"IdCategoriaOdoo": record.odoo_id.id}

    @changed_by("name")
    @mapping
    def Descripcion(self, record):
        return {
            "Descripcion": record.with_context(
                lang=self.backend_record.lang_id.code
            ).name[:255]
        }
