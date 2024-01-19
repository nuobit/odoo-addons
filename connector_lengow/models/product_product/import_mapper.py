# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ProductProductImportMapper(Component):
    _name = "lengow.product.product.import.mapper"
    _inherit = "lengow.import.mapper"

    _apply_on = "lengow.product.product"

    direct = [("sku", "default_code")]

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}
