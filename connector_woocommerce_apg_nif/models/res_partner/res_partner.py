# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    woocommerce_vat_compact = fields.Char(
        string="Compact Tax ID",
        compute="_compute_woocommerce_vat_compact",
        store=True,
        index=True,
        help="The Tax ID in upper case, without spaces, dots or dashes, for the "
        "WooCommerce import to find a customer by its NIF however it was typed.",
    )

    @api.model
    def _woocommerce_compact_vat(self, vat):
        return re.sub("[^A-Za-z0-9]", "", vat).upper()

    @api.depends("vat")
    def _compute_woocommerce_vat_compact(self):
        for rec in self:
            rec.woocommerce_vat_compact = (
                self._woocommerce_compact_vat(rec.vat) if rec.vat else False
            )

    @api.model
    def _woocommerce_vat_forms(self, vat):
        """The compact forms the VAT number ``vat`` may be stored in: as it is
        and, when it starts with a country code, without it."""
        compact = self._woocommerce_compact_vat(vat)
        vat_country, vat_number = self._split_vat(compact)
        has_country_code = bool(
            self.env["res.country"].search_count([("code", "=", vat_country.upper())])
        )
        return [compact, vat_number] if has_country_code else [compact]

    def _woocommerce_is_valid_vat(self, vat, country):
        """Whether Odoo accepts ``vat`` as the VAT number of a company in
        ``country``, with its own check."""
        try:
            self.new(
                {"vat": vat, "country_id": country.id, "company_type": "company"}
            ).check_vat()
        except ValidationError:
            return False
        return True

    @api.model
    def _woocommerce_vat_number(self, nif, country, fallback_country):
        """The VAT number of a checkout's ``nif``: with the code of the
        billing ``country``, else, when Odoo refuses it so, with the code of
        ``fallback_country``. Refused with both, the first, which Odoo refuses
        when the customer is created."""
        vat = self.fix_eu_vat_number(country.id, nif)
        fallback_vat = self.fix_eu_vat_number(fallback_country.id, nif)
        keeps_vat = self._woocommerce_is_valid_vat(
            vat, country
        ) or not self._woocommerce_is_valid_vat(fallback_vat, fallback_country)
        return vat if keeps_vat else fallback_vat

    def _get_hash_fields(self):
        hash_fields = super()._get_hash_fields()
        return hash_fields + ["vat"]

    @api.depends("vat")
    def _compute_address_hash(self):
        super()._compute_address_hash()

    def _set_values_hash(self):
        for rec in self:
            values = super()._set_values_hash()
            values.append(rec.vat or None)
            return values
