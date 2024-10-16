# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductTemplateImporter(Component):
    _name = "woocommerce.wpml.product.template.record.direct.importer"
    _inherit = "woocommerce.wpml.record.direct.importer"

    _apply_on = "woocommerce.wpml.product.template"
