# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class SaleOrderLineBatchImporter(Component):
    """Import the Ambugest Services.

    For every sale order in the list, a delayed job is created.
    """

    _name = "ambugest.sale.order.line.delayed.batch.importer"
    _inherit = "ambugest.delayed.batch.importer"
    _apply_on = "ambugest.sale.order.line"


class SaleOrderLineImporter(Component):
    _name = "ambugest.sale.order.line.importer"
    _inherit = "ambugest.importer"
    _apply_on = "ambugest.sale.order.line"

    def _import_dependencies(self):
        external_id = (self.external_data["EMPRESA"], self.external_data["Articulo"])

        self._import_dependency(external_id, "ambugest.product.product", always=True)
