# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    openupgrade.m2o_to_x2m(
        env.cr,
        env['lighting.product'],
        'lighting_product',
        'application_ids',
        openupgrade.get_legacy_name('application_id'),
    )