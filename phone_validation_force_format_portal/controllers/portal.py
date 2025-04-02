# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.phone_validation.tools.phone_validation import phone_parse
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation)
        for field in ["phone", "mobile"]:
            try:
                if data.get(field):
                    phone_parse(data[field], False)  # phone number validation
            except Exception:
                error[field] = "error"
                error_message.append(
                    _(
                        "Invalid %s number. Please use the format:\n"
                        "+[Country Code][Number]\n"
                        "Example: +34612345758"
                    )
                    % _(field)
                )
        return error, error_message
