# -*- coding: utf-8 -*-
# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def migrate(cr, version):
    if not version:
        return

    from openupgradelib import openupgrade

    ### rename model
    openupgrade.rename_models(
        cr, [('lighting.product.leddriver', 'lighting.product.ledchip'),
        ]
    )

    ### rename DB
    # rename table and sequence
    openupgrade.rename_tables(
        cr, [('lighting_product_leddriver', 'lighting_product_ledchip')]
    )

    # rename constraints
    cr.execute(
        "COMMENT ON TABLE lighting_product_ledchip "
        "IS 'lighting.product.ledchip'"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_leddriver_uniq "
        "TO lighting_product_ledchip_ledchip_uniq"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_pkey "
        "TO lighting_product_ledchip_pkey"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_brand_id_fkey "
        "TO lighting_product_ledchip_brand_id_fkey"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_create_uid_fkey "
        "TO lighting_product_ledchip_create_uid_fkey"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_product_id_fkey "
        "TO lighting_product_ledchip_product_id_fkey"
    )

    cr.execute(
        "ALTER TABLE lighting_product_ledchip "
        "RENAME CONSTRAINT lighting_product_leddriver_write_uid_fkey "
        "TO lighting_product_ledchip_write_uid_fkey"
    )
