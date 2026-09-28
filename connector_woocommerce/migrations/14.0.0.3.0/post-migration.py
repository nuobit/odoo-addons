# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Both image lists previously used the template setting. Preserve that
    # choice until the user deliberately configures the variant policy.
    backends = env["woocommerce.backend"].with_context(active_test=False).search([])
    for backend in backends:
        backend.use_main_product_variant_image = backend.use_main_product_image
