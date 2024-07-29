# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueExporter(Component):
    _name = "woocommerce.product.attribute.value.record.direct.exporter"
    _inherit = [
        "woocommerce.product.attribute.value.record.direct.exporter",
        "woocommerce.product.wpml.mixin.record.direct.exporter",
    ]

    def run(self, relation, always=True, internal_fields=None):
        return self.wpml_run(relation, always=always, internal_fields=internal_fields)