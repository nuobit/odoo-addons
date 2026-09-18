# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceBinder(AbstractComponent):
    _name = "woocommerce.binder"
    _inherit = ["connector.extension.binder", "base.woocommerce.connector"]

    _default_binding_field = "woocommerce_bind_ids"
