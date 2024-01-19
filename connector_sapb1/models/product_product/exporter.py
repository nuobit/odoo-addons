# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductDelayedBatchExporter(Component):
    """Export the SAP B1 Product.

    For every product in the list, a delayed job is created.
    """

    _name = "sapb1.product.product.delayed.batch.exporter"
    _inherit = "sapb1.delayed.batch.exporter"

    _apply_on = "sapb1.product.product"


class ProductProductDirectBatchExporter(Component):
    """Export the SAP B1 Products.

    For every partner in the list, export it directly.
    """

    _name = "sapb1.product.product.direct.batch.exporter"
    _inherit = "sapb1.direct.batch.exporter"

    _apply_on = "sapb1.product.product"


class ProductProductExporter(Component):
    _name = "sapb1.product.product.exporter"
    _inherit = "sapb1.exporter"

    _apply_on = "sapb1.product.product"
