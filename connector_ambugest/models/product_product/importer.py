# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ProductProductBatchImporter(Component):
    """Import the Ambugest Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "ambugest.product.product.delayed.batch.importer"
    _inherit = "ambugest.delayed.batch.importer"
    _apply_on = "ambugest.product.product"


class ProductProductImporter(Component):
    _name = "ambugest.product.product.importer"
    _inherit = "ambugest.importer"
    _apply_on = "ambugest.product.product"

    # def _import_dependencies(self):
    #     external_id = (self.external_data['CodigoEmpresa'], self.external_data['CodigoEmpleado'])
    #
    #     self._import_dependency(external_id, 'ambugest.res.partner', always=True)
