# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestResPartnerVatForms(SavepointCase):
    def test_vat_number_with_a_country_code_is_also_searched_without_it(self):
        self.assertEqual(
            self.env["res.partner"]._woocommerce_vat_forms("es-b 12345674"),
            ["ESB12345674", "B12345674"],
        )

    def test_nie_letter_is_not_taken_for_a_country_code(self):
        self.assertEqual(
            self.env["res.partner"]._woocommerce_vat_forms("X1234567L"),
            ["X1234567L"],
        )

    def test_vat_number_is_kept_in_upper_case_without_separators(self):
        partner = self.env["res.partner"].create(
            {"name": "WooCommerce clinic", "vat": "b-1234 5674"}
        )
        self.assertEqual(partner.woocommerce_vat_compact, "B12345674")
