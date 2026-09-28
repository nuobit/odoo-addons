# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceCase


class TestImagePolicyMigration(WooCommerceCase):
    def test_upgrade_preserves_existing_image_choices(self):
        self.backend.write(
            {"use_main_product_image": "no", "use_main_product_variant_image": "first"}
        )
        first = self.backend.copy(
            {
                "use_main_product_image": "first",
                "use_main_product_variant_image": "last",
            }
        )
        last = self.backend.copy(
            {
                "use_main_product_image": "last",
                "use_main_product_variant_image": "first",
                "active": False,
            }
        )
        unset = self.backend.copy(
            {"use_main_product_image": False, "use_main_product_variant_image": "first"}
        )
        jobs = self.env["queue.job"].search([])

        self._run_migration("connector_woocommerce", "14.0.0.3.0", "14.0.0.2.2")
        self.env["woocommerce.backend"].flush()

        self.assertEqual(self.backend.use_main_product_image, "no")
        self.assertEqual(self.backend.use_main_product_variant_image, "no")
        self.assertEqual(first.use_main_product_image, "first")
        self.assertEqual(first.use_main_product_variant_image, "first")
        self.assertEqual(last.use_main_product_image, "last")
        self.assertEqual(last.use_main_product_variant_image, "last")
        self.assertFalse(last.active)
        self.assertFalse(unset.use_main_product_image)
        self.assertFalse(unset.use_main_product_variant_image)
        self.assertEqual(self.env["queue.job"].search([]), jobs)

    def test_new_backend_defaults_to_first_for_both_image_lists(self):
        defaults = self.env["woocommerce.backend"].default_get(
            ["use_main_product_image", "use_main_product_variant_image"]
        )

        self.assertEqual(defaults["use_main_product_image"], "first")
        self.assertEqual(defaults["use_main_product_variant_image"], "first")
