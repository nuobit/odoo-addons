# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # remove is_accessory field from product type
    openupgrade.drop_columns(
        env.cr,
        [('lighting_product_type', 'is_accessory'),
        ]
    )
