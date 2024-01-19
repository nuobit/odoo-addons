# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class CountryStateImportMapper(Component):
    _name = "lengow.res.country.state.import.mapper"
    _inherit = "lengow.import.mapper"

    _apply_on = "lengow.res.country.state"

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def name(self, record):
        return {
            "name": record["state_region"],
        }

    @only_create
    @mapping
    def code(self, record):
        return {
            "code": record["state_region"],
        }

    @only_create
    @mapping
    def country(self, record):
        country_code = record["common_country_iso_a2"]
        if country_code:
            country = self.env["res.country"].search([("code", "=", country_code)])
            if not country:
                raise ValidationError(
                    _("Country %s not found on odoo. Please, create it before import")
                    % record["common_country_iso_a2"]
                )
            return {"country_id": country.id}
        else:
            return {"country_id": None}
