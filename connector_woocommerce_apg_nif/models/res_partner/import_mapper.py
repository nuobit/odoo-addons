# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceResPartnerImportMapper(Component):
    _inherit = "woocommerce.res.partner.import.mapper"

    @mapping
    def vat(self, record):
        return {"vat": record.get("nif")}
