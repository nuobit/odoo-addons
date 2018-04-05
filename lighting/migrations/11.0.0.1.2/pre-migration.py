# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    ### rename first lampholder
    openupgrade.rename_fields(
        env, [('lighting.product.source', 'lighting_product_source',
               'lampholder_id', 'lampholder_technical_id'),
        ]
    )

    env.cr.execute(
        "COMMENT ON COLUMN lighting_product_source.lampholder_technical_id "
        "IS 'Technical lampholder'"
    )

    env.cr.execute(
        "ALTER TABLE lighting_product_source "
        "RENAME CONSTRAINT lighting_product_source_lampholder_id_fkey "
        "TO lighting_product_source_lampholder_technical_id_fkey"
    )

    ### rename second lampholder
    openupgrade.rename_fields(
        env, [('lighting.product.source', 'lighting_product_source',
               'lampholder_marketing_id', 'lampholder_id'),
        ]
    )

    env.cr.execute(
        "COMMENT ON COLUMN lighting_product_source.lampholder_id "
        "IS 'Lampholder'"
    )

    env.cr.execute(
        "ALTER TABLE lighting_product_source "
        "RENAME CONSTRAINT lighting_product_source_lampholder_marketing_id_fkey "
        "TO lighting_product_source_lampholder_id_fkey"
    )