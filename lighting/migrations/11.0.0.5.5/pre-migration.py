# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    ## rename field
    openupgrade.rename_fields(
        env, [('lighting.product', 'lighting_product',
               'auxiliary_equipment_model_id', 'auxiliary_equipment_brand_id'),
        ]
    )

    ### rename model
    openupgrade.rename_models(
        env.cr, [('lighting.product.auxiliaryequipmentmodel', 'lighting.product.auxiliaryequipmentbrand'),
        ]
    )

    ### rename external ids
    openupgrade.rename_xmlids(
        env.cr, [('lighting.product_auxiliaryequipmentmodel_elt', 'lighting.product_auxiliaryequipmentbrand_elt'),
                 ('lighting.product_auxiliaryequipmentmodel_meanwell', 'lighting.product_auxiliaryequipmentbrand_meanwell'),
                 ('lighting.product_auxiliaryequipmentmodel_tci', 'lighting.product_auxiliaryequipmentbrand_tci'),
                 ('lighting.product_auxiliaryequipmentmodel_tecnotrafo', 'lighting.product_auxiliaryequipmentbrand_tecnotrafo'),
                 ('lighting.product_auxiliaryequipmentmodel_tridonic', 'lighting.product_auxiliaryequipmentbrand_tridonic'),
        ]
    )

    ### rename DB
    ## lighting_product_auxiliaryequipmentmodel
    # rename table and sequence
    openupgrade.rename_tables(
        env.cr, [('lighting_product_auxiliaryequipmentmodel', 'lighting_product_auxiliaryequipmentbrand')]
    )

    # rename comments
    env.cr.execute(
        "COMMENT ON TABLE lighting_product_auxiliaryequipmentbrand "
        "IS 'lighting.product.auxiliaryequipmentbrand'"
    )

    env.cr.execute(
        "COMMENT ON COLUMN lighting_product_auxiliaryequipmentbrand.name "
        "IS 'Auxiliary equipment brand'"
    )

    # rename uniq keys
    env.cr.execute(
        "ALTER TABLE lighting_product_auxiliaryequipmentbrand "
        "RENAME CONSTRAINT lighting_product_auxiliaryequipmentmodel_name_uniq "
        "TO lighting_product_auxiliaryequipmentbrand_name_uniq"
    )

    # rename pkeys
    env.cr.execute(
        "ALTER TABLE lighting_product_auxiliaryequipmentbrand "
        "RENAME CONSTRAINT lighting_product_auxiliaryequipmentmodel_pkey "
        "TO lighting_product_auxiliaryequipmentbrand_pkey"
    )

    # rename fkeys
    env.cr.execute(
        "ALTER TABLE lighting_product_auxiliaryequipmentbrand "
        "RENAME CONSTRAINT lighting_product_auxiliaryequipmentmodel_create_uid_fkey "
        "TO lighting_product_auxiliaryequipmentbrand_create_uid_fkey"
    )

    env.cr.execute(
        "ALTER TABLE lighting_product_auxiliaryequipmentbrand "
        "RENAME CONSTRAINT lighting_product_auxiliaryequipmentmodel_write_uid_fkey "
        "TO lighting_product_auxiliaryequipmentbrand_write_uid_fkey"
    )

    ## lighting_product
    # rename comments
    env.cr.execute(
        "COMMENT ON COLUMN lighting_product.auxiliary_equipment_brand_id "
        "IS 'Auxiliary equipment brand'"
    )

    # rename fkeys
    env.cr.execute(
        "ALTER TABLE lighting_product "
        "RENAME CONSTRAINT lighting_product_auxiliary_equipment_model_id_fkey "
        "TO lighting_product_auxiliary_equipment_brand_id_fkey"
    )
