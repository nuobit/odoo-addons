# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class LengowProductProductBatchDirectImporter(Component):
    """Import the Lengow Partners.

    For every partner in the list, import it directly.
    """

    _name = "lengow.product.product.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "lengow.product.product"


class LengowProductProductBatchDelayedImporter(Component):
    """Import the lengow Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "lengow.product.product.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "lengow.product.product"


class LengowProductProductImporter(Component):
    _name = "lengow.product.product.record.direct.importer"
    _inherit = "lengow.record.direct.importer"

    _apply_on = "lengow.product.product"

    def run(self, external_id, sync_date, external_data=None, external_fields=None):
        if not external_data:
            raise ValidationError(_("External data is mandatory"))
        return super().run(external_id, sync_date, external_data=external_data)
