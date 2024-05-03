# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class SaleOrderImporter(Component):
    _inherit = "oxigesti.sale.order.importer"

    def _after_import(self, binding):
        super()._after_import(binding.with_context(skip_reserved_quantity=True))
