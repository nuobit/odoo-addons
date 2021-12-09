# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class ProductProductExportMapper(Component):
    _name = "oxigesti.product.product.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.product.product"

    direct = [
        (nullif("barcode"), "CodigoAlternativo"),
        ("list_price", "Importe"),
    ]

    @only_create
    @mapping
    def CodigoArticulo(self, record):
        default_code = (
            record.default_code
            and record.default_code.strip()
            and record.default_code
            or None
        )
        if default_code:
            if record.default_code != record.default_code.strip():
                raise AssertionError(
                    "The Odoo product with Name '%s' has Internal reference "
                    " with leading or trailing spaces '%s'. "
                    "Please remove these spaces and requeue the job."
                    % (record.name, record.default_code)
                )
        else:
            raise AssertionError(
                "The Odoo product with ID %i and Name '%s' "
                "has no Internal reference. "
                "Please assign one and requeue the job." % (record.id, record.name)
            )

        return {"CodigoArticulo": record.default_code}

    @changed_by("name")
    @mapping
    def DescripcionArticulo(self, record):
        return {
            "DescripcionArticulo": record.with_context(
                lang=self.backend_record.lang_id.code
            ).name[:250]
        }

    @changed_by("categ_id")
    @mapping
    def Categoria(self, record):
        category = record.categ_id
        binder = self.binder_for("oxigesti.product.category")
        external_id = binder.to_external(category, wrap=True)
        assert external_id, (
            "%s: There's no bond between Odoo category and "
            "Oxigesti category, so the Oxigesti ID cannot be obtained. "
            "At this stage, the Oxigesti category should have been linked via "
            "ProductCategory._export_dependencies. "
            "If not, then this category %s (%s) does not exist in Oxigesti."
            % (category, category, category.display_name)
        )

        return {"Categoria": external_id[0]}

    @changed_by("active")
    @mapping
    def Archivado(self, record):
        return {
            "Archivado": not (
                record.odoo_id.active and record.odoo_id.product_tmpl_id.active
            )
        }

    @mapping
    def Eliminado(self, record):
        return {"Eliminado": 0}
