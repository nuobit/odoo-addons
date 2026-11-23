# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestSimplifiedInvoiceCustomer(TestPointOfSaleHttpCommon):
    @classmethod
    def _get_main_company(cls):
        # A Spanish company, as l10n_es_pos's own tour test sets it up
        cls.company_data["company"].country_id = cls.env.ref("base.es").id
        cls.company_data["company"].currency_id = cls.env.ref("base.EUR").id
        cls.company_data["company"].vat = "ESA12345674"
        return cls.company_data["company"]

    def test_simplified_invoice_customer(self):
        self.env["res.partner"].create(
            {
                "name": "Customer Without Tax ID",
                "street": "Main Street 1",
                "city": "Barcelona",
                "country_id": self.env.ref("base.es").id,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Customer Not Subject To Tax",
                "vat": "/",
                "street": "New Street 1",
                "city": "Vic",
                "country_id": self.env.ref("base.es").id,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Customer With Tax ID",
                "vat": "ES12345678Z",
                "street": "New Street 2",
                "city": "Girona",
                "country_id": self.env.ref("base.es").id,
            }
        )
        self.main_pos_config.l10n_es_simplified_invoice_journal_id = self.env[
            "account.journal"
        ].create(
            {
                "name": "Simplified Invoice Journal",
                "type": "sale",
                "company_id": self._get_main_company().id,
                "code": "SIMP",
            }
        )
        # The tour looks for the ticket's texts in English
        self.pos_user.lang = "en_US"
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_tour(
            f"/pos/ui?config_id={self.main_pos_config.id}",
            "l10n_es_pos_simplified_invoice_customer_tour",
            login="pos_user",
        )
