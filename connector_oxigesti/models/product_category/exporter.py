# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ProductCategoryBatchExporter(Component):
    """Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.product.category.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    _apply_on = "oxigesti.product.category"


class ProductCategoryExporter(Component):
    _name = "oxigesti.product.category.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.product.category"
