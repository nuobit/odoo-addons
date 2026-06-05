# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.urls import url_encode

from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestStockProductService(HttpCase):
    def setUp(self):
        super().setUp()
        self.password = "stock_rest_test"
        self.api_user = new_test_user(
            self.env,
            login="stock_rest_test_user",
            password=self.password,
            groups="base.group_user",
            context={"no_reset_password": True},
            lang="en_US",
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product_categ = self.env.ref("product.product_category_all")

        self.product_code_a = self._create_stocked_product(
            "GJR REST Coded A",
            default_code="GJR-REST-A",
            barcode="GJR-REST-A-BARCODE",
        )
        self.product_code_b = self._create_stocked_product(
            "GJR REST Coded B",
            default_code="GJR-REST-B",
            barcode="GJR-REST-B-BARCODE",
        )
        self.product_without_code = self._create_stocked_product(
            "GJR REST Without Code",
            barcode="GJR-REST-NO-CODE",
        )
        self.test_products = (
            self.product_code_a | self.product_code_b | self.product_without_code
        )

    def _create_stocked_product(self, name, default_code=None, barcode=None):
        vals = {
            "name": name,
            "type": "product",
            "categ_id": self.product_categ.id,
        }
        if default_code is not None:
            vals["default_code"] = default_code
        if barcode is not None:
            vals["barcode"] = barcode
        product = self.env["product.product"].create(vals)
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 1
        )
        return product

    def _get_products(self, **params):
        self.authenticate(self.api_user.login, self.password)
        query_string = "?{}".format(url_encode(params)) if params else ""
        response = self.url_open("/api/v2/products{}".format(query_string))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        return response.json()

    def _get_test_product_rows(self, rows):
        test_product_ids = set(self.test_products.ids)
        return [row for row in rows if row["id"] in test_product_ids]

    def test_products_endpoint_sorts_products_without_code_last(self):
        rows = self._get_products()
        test_product_rows = self._get_test_product_rows(rows)

        self.assertEqual(
            [row["id"] for row in test_product_rows],
            [
                self.product_code_a.id,
                self.product_code_b.id,
                self.product_without_code.id,
            ],
        )

        product_without_code_row = test_product_rows[-1]
        self.assertIsNone(product_without_code_row["code"])
        self.assertEqual(product_without_code_row["barcode"], "GJR-REST-NO-CODE")
        self.assertTrue(product_without_code_row["lots"])

    def test_products_endpoint_filters_by_code(self):
        rows = self._get_products(code=self.product_code_b.default_code)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], self.product_code_b.id)
        self.assertEqual(rows[0]["code"], self.product_code_b.default_code)

    def test_products_endpoint_filters_by_barcode_without_code(self):
        rows = self._get_products(barcode=self.product_without_code.barcode)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], self.product_without_code.id)
        self.assertIsNone(rows[0]["code"])
        self.assertEqual(rows[0]["barcode"], self.product_without_code.barcode)
