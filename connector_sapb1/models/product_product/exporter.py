# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SAPB1ProductProductBatchDirectExporter(Component):
    """Export the SAP B1 Products.

    For every partner in the list, export it directly.
    """

    _name = "sapb1.product.product.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "sapb1.product.product"


class SAPB1ProductProductBatchDelayedExporter(Component):
    """Export the SAP B1 Product.

    For every product in the list, a delayed job is created.
    """

    _name = "sapb1.product.product.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "sapb1.product.product"


class SAPB1ProductProductExporter(Component):
    _name = "sapb1.product.product.record.direct.exporter"
    _inherit = "sapb1.record.direct.exporter"

    _apply_on = "sapb1.product.product"
