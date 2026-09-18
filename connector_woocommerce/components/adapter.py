# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
            timeout=30,
        )

    def _prepare_product_price_conversion_mapper(self):
        """Return the product price and sale date converters for WooCommerce."""
        # A number is sent as text. None is "no value" in Odoo, and WooCommerce
        # clears a field with "": that is what a None becomes here.
        return {
            "/regular_price": lambda x: str(round(x, 10)) if x is not None else "",
            "/sale_price": lambda x: str(round(x, 10)) if x is not None else "",
            "/date_on_sale_from_gmt": lambda x: x if x is not None else "",
            "/date_on_sale_to_gmt": lambda x: x if x is not None else "",
        }

    def _format_product(self, data):
        conv_mapper = self._prepare_product_price_conversion_mapper()
        self._convert_format(data, conv_mapper)

    def prepare_meta_data(self, data):
        meta_data = []
        for field in self._prepare_meta_data_fields():
            if field in data:
                meta_data.append({"key": field, "value": data[field]})
                data.pop(field)
        return meta_data

    def _prepare_meta_data_fields(self):
        return []
