# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class WooCommerceWPMLBinder(AbstractComponent):
    _name = "woocommerce.wpml.binder"
    _inherit = ["connector.extension.generic.binder", "base.woocommerce.wpml.connector"]

    _default_binding_field = "woocommerce_wpml_bind_ids"
