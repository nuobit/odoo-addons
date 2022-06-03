# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component

from ..common import tools


class ProductSupplierinfoBinder(Component):
    _name = "veloconnect.product.brand.binder"
    _inherit = "veloconnect.binder"

    _apply_on = "veloconnect.product.brand"

    _external_field = "ManufacturersItemIdentificationName"
    _internal_field = "veloconnect_manufacturer_name"

    _internal_alt_field = "name"

    def _get_internal_record_domain(self, value):
        return [("name_slug", "=", tools.slugify(value["name"]))]
