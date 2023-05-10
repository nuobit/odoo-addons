# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceResPartnerImportMapper(Component):
    _name = "woocommerce.res.partner.import.mapper"
    _inherit = "woocommerce.import.mapper"

    _apply_on = "woocommerce.res.partner"

    @mapping
    def name(self, record):
        return {"name": record.get("first_name") + " " + record.get("last_name")}

    # TODO: debug
    @mapping
    def parent_id(self, record):
        return {"parent_id": record.get("parent") or None}

    @mapping
    def street(self, record):
        return {"street": record.get("address_1")}

    @mapping
    def street2(self, record):
        return {"street2": record.get("address_2")}

    @mapping
    def city(self, record):
        return {"city": record.get("city")}

    @mapping
    def type(self, record):
        address_type = record.get("type")
        if address_type == "billing":
            return {"type": "invoice"}
        elif address_type == "shipping":
            return {"type": "delivery"}
        return {"type": record.get("type")}

    @mapping
    def state_id(self, record):
        # TODO: mirar com tracten els states a lengow. Import dependency del state?
        state = self.env["res.country.state"].search(
            [("code", "=", "B"), ("country_id.code", "=", "ES")]
        )
        if state:
            return {"state_id": state.id}

    @mapping
    def zip(self, record):
        return {"zip": record.get("postcode")}

    @mapping
    def country_id(self, record):
        country = self.env["res.country"].search([("code", "=", record.get("country"))])
        if country:
            return {"country_id": country.id or None}

    @mapping
    def email(self, record):
        return {"email": record.get("email")}

    @mapping
    def mobile(self, record):
        return {"mobile": record.get("phone")}


# woocommerce
# first_name    x
# last_name     x
# company       x
# address_1     x
# address_2     x
# city          x
# state         x
# postcode      x
# country       x
# email         x
# phone         x
