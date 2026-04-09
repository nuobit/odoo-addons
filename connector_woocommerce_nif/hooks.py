# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


def pre_init_hook(env):
    if openupgrade.is_module_installed(env.cr, "connector_woocommerce_apg_nif"):
        openupgrade.update_module_names(
            env.cr,
            [("connector_woocommerce_apg_nif", "connector_woocommerce_nif")],
            merge_modules=True,
        )
