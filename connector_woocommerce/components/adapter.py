# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from woocommerce import API as API

from odoo.addons.component.core import AbstractComponent


class ConnectorWooCommerceAdapter(AbstractComponent):
    _name = "connector.woocommerce.adapter"
    _inherit = [
        "connector.extension.woocommerce.adapter.crud",
        "base.woocommerce.connector",
    ]

    _description = "WooCommerce Adapter (abstract)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wcapi = API(
            url=self.backend_record.url,
            consumer_key=self.backend_record.consumer_key,
            consumer_secret=self.backend_record.consumer_secret,
            version="wc/v3",
            verify_ssl=self.backend_record.verify_ssl,
        )
