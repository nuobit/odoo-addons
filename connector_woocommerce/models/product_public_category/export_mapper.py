# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceProductPublicCategoryExportMapper(Component):
    _name = "woocommerce.product.public.category.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.public.category"

    direct = [
        ("name", "name"),
    ]

    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.public.category")
        if record.parent_id:
            values = binder.get_external_dict_ids(record.parent_id)
            return {"parent": values["id"]}
