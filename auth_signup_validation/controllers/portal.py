# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.portal.controllers.portal import CustomerPortal

CustomerPortal.MANDATORY_BILLING_FIELDS.extend(["lang"])


class CustomerPortal(CustomerPortal):
    def details_form_validate(self, data, partner_creation=False):
        if "language" in data:
            data["lang"] = data.pop("language")
        return super().details_form_validate(data, partner_creation)
