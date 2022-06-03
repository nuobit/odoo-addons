# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductBrandDelayedBatchImporter(Component):
    """Import the Veloconnect Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "veloconnect.product.brand.delayed.batch.importer"
    _inherit = "veloconnect.delayed.batch.importer"

    _apply_on = "veloconnect.product.brand"


class ProductBrandDirectBatchImporter(Component):
    """Import the Veloconnect Partners.

    For every partner in the list, import it directly.
    """

    _name = "veloconnect.product.brand.direct.batch.importer"
    _inherit = "veloconnect.direct.batch.importer"

    _apply_on = "veloconnect.product.brand"


class ProductBrandImporter(Component):
    _name = "veloconnect.product.brand.importer"
    _inherit = "veloconnect.importer"

    _apply_on = "veloconnect.product.brand"

    def _create(self, values):
        with self._retry_unique_violation():
            return super()._create(values)
