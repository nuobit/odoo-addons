# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import Mock

from odoo.exceptions import ValidationError

from .common import WooCommerceCase


class TestAdapterErrors(WooCommerceCase):
    def test_update_of_category_deleted_in_woocommerce_explains_what_to_do(self):
        response = Mock(ok=False, status_code=404)
        response.json.return_value = {
            "code": "woocommerce_rest_term_invalid",
            "message": "Resource does not exist.",
            "data": {"status": 404},
        }
        with self.backend.work_on("woocommerce.product.public.category") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.wcapi = Mock(put=Mock(return_value=response))
            with self.assertRaises(ValidationError) as error:
                adapter.write([2001], {"name": "Masks"})
        self.assertEqual(
            error.exception.args[0],
            "Could not update products/categories/2001 because it was deleted from "
            "WooCommerce. What Odoo sends to WooCommerce should not be deleted. For "
            "each record it sends, Odoo keeps one link per language. As long as the "
            "language links of this record exist, every update from Odoo will fail. "
            "If you really do not want it in WooCommerce, delete in Odoo all the "
            "language links of this record: if one remains, Odoo will keep trying. "
            "If no product uses it, Odoo will not send it again; if a product uses "
            "it, now or some day, it will go back to WooCommerce when that product "
            "is exported.",
        )

    def test_delete_of_category_deleted_in_woocommerce_keeps_the_generic_error(self):
        response = Mock(ok=False, status_code=404)
        response.json.return_value = {
            "code": "woocommerce_rest_term_invalid",
            "message": "Resource does not exist.",
            "data": {"status": 404},
        }
        with self.backend.work_on("woocommerce.product.public.category") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.wcapi = Mock(delete=Mock(return_value=response))
            with self.assertRaisesRegex(
                ValidationError, "Op: delete, Resource: products/categories/2001,"
            ):
                adapter.delete([2001])

    def test_update_of_category_whose_parent_was_deleted_names_the_parent(self):
        response = Mock(ok=False, status_code=500)
        response.json.return_value = {
            "code": "missing_parent",
            "message": "Parent term does not exist.",
            "data": None,
        }
        with self.backend.work_on("woocommerce.product.public.category") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.wcapi = Mock(put=Mock(return_value=response))
            with self.assertRaises(ValidationError) as error:
                adapter.write([2001], {"name": "Masks", "parent": 2000})
        self.assertEqual(
            error.exception.args[0],
            'Could not send "Masks" because its parent, products/categories/2000, '
            "was deleted from WooCommerce. What Odoo sends to WooCommerce should "
            "not be deleted. For each record it sends, Odoo keeps one link per "
            "language. Delete in Odoo all the language links of the parent: Odoo "
            "will create it again in WooCommerce the next time it sends this "
            "record. If you do not want the parent in WooCommerce, change the "
            "parent of this record in Odoo.",
        )

    def test_create_of_category_whose_parent_was_deleted_names_the_parent(self):
        response = Mock(ok=False, status_code=400)
        response.json.return_value = {
            "code": "missing_parent",
            "message": "Parent term does not exist.",
            "data": {"status": 400},
        }
        with self.backend.work_on("woocommerce.product.public.category") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.wcapi = Mock(post=Mock(return_value=response))
            with self.assertRaises(ValidationError) as error:
                adapter.create({"name": "Masks", "parent": 2000})
        self.assertEqual(
            error.exception.args[0],
            'Could not send "Masks" because its parent, products/categories/2000, '
            "was deleted from WooCommerce. What Odoo sends to WooCommerce should "
            "not be deleted. For each record it sends, Odoo keeps one link per "
            "language. Delete in Odoo all the language links of the parent: Odoo "
            "will create it again in WooCommerce the next time it sends this "
            "record. If you do not want the parent in WooCommerce, change the "
            "parent of this record in Odoo.",
        )
