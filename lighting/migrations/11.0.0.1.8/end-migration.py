# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # remove type_id from product
    openupgrade.drop_columns(
        env.cr,
        [('lighting_product', openupgrade.get_legacy_name('type_id')),
         ]
    )