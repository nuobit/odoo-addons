# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ProductProductDelayedBatchImporter(Component):
    """Import the lengow Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "lengow.product.product.delayed.batch.importer"
    _inherit = "lengow.delayed.batch.importer"

    _apply_on = "lengow.product.product"


class ProductProductDirectBatchImporter(Component):
    """Import the Lengow Partners.

    For every partner in the list, import it directly.
    """

    _name = "lengow.product.product.direct.batch.importer"
    _inherit = "lengow.direct.batch.importer"

    _apply_on = "lengow.product.product"


class ProductProductImporter(Component):
    _name = "lengow.product.product.importer"
    _inherit = "lengow.importer"

    _apply_on = "lengow.product.product"

    def run(self, external_id, external_data, external_fields=None):
        if not external_data:
            raise ValidationError("External data is mandatory")
        return super().run(external_id, external_data=external_data)
