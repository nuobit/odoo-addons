# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class WooCommerceBinder(AbstractComponent):
    _name = "woocommerce.binder"
    _inherit = ["connector.extension.generic.binder", "base.woocommerce.connector"]

    _default_binding_field = "woocommerce_bind_ids"
