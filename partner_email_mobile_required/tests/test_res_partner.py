# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def test_contact_details_are_required_for_regular_records(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({"name": "Regular partner"})

    def test_module_data_can_create_technical_partner(self):
        partner = (
            self.env["res.partner"]
            .with_context(install_module="test_module")
            .create({"name": "Technical partner"})
        )

        self.assertTrue(partner.exists())
        self.assertFalse(partner.email)
        self.assertFalse(partner.mobile)
