# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    fields = [
        'novelty',
        'cataloged',
        'discontinued_by_supplier',
        'until_end_stock',
        'discontinued',
    ]

    openupgrade.drop_columns(
        env.cr,
        [('lighting_product', '%s' % f) for f in fields]
    )
