# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceCase


class TestImagePolicyMigration(WooCommerceCase):
    def test_new_backend_defaults_to_first_for_both_image_lists(self):
        defaults = self.env["woocommerce.backend"].default_get(
            ["use_main_product_image", "use_main_product_variant_image"]
        )

        self.assertEqual(defaults["use_main_product_image"], "first")
        self.assertEqual(defaults["use_main_product_variant_image"], "first")
