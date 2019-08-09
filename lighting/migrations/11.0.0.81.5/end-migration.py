# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    fields = [
        'corrosion_resistance',
        'recessing_box_included',
        'periodic_maintenance',
        'anchorage_included',
        'post_included',
        'post_with_inspection_chamber',
        'emergency_light',
        'flammable_surfaces',
        'mechanical_screwdriver',
    ]

    openupgrade.drop_columns(
        env.cr,
        [('lighting_product', '%s_moved0' % f) for f in fields]
    )
