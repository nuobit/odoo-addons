# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo.tests.common import SavepointCase


class CommonAccountMultiVat(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(CommonAccountMultiVat, cls).setUpClass()

        # MODELS
        cls.user_type = cls.env.ref("account.data_account_type_current_assets")
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Customer Invoices 2",
                "type": "sale",
                "code": "test_INV2",
            }
        )
        cls.date = datetime.strptime("2022-01-13", "%Y-%m-%d").date()
        cls.account_100 = cls.env["account.account"].create(
            {
                "name": "Test Account 100",
                "code": "test_100000",
                "user_type_id": cls.user_type.id,
            }
        )
        cls.account_empty = cls.env["account.account"]
        cls.account_7000 = cls.env["account.account"].create(
            {
                "name": "Test Account 7000",
                "code": "test_700000",
                "user_type_id": cls.user_type.id,
            }
        )
        cls.tax_sale = cls.env["account.tax"].create(
            {"name": "Sale tax", "type_tax_use": "sale", "amount": "20.00"}
        )
        cls.account_205 = cls.env["account.account"].create(
            {
                "name": "Test Account 2050",
                "code": "test_205000",
                "user_type_id": cls.user_type.id,
            }
        )
        cls.accrual_account_id = cls.env["account.account"].create(
            {
                "name": "Test Account 4309",
                "code": "test_430902",
                "user_type_id": cls.user_type.id,
            }
        )
        cls.setting = cls.env["res.config.settings"].create(
            {
                "accrual_account_id": cls.accrual_account_id.id,
                "accrual_asset_account_type_id": cls.env.ref(
                    "account.data_account_type_fixed_assets"
                ).id,
            }
        )
        cls.product_template_205 = cls.env["product.template"].create(
            {
                "name": "New Product 205",
                "type": "service",
                "property_account_income_id": cls.account_205.id,
                "taxes_id": [(6, 0, [cls.tax_sale.id])],
                "lst_price": "100",
            }
        )
        cls.product_template_7000 = cls.env["product.template"].create(
            {
                "name": "New Product 7000",
                "type": "service",
                "property_account_income_id": cls.account_7000.id,
                "taxes_id": [(6, 0, [cls.tax_sale.id])],
                "lst_price": "100",
            }
        )
        cls.product_205 = cls.product_template_205.product_variant_id
        cls.product_7000 = cls.product_template_7000.product_variant_id
