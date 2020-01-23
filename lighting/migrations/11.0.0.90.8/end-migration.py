# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    fields = [
        'input_current',
        'output_current',
    ]

    openupgrade.drop_columns(
        env.cr,
        [('lighting_product', '%s_moved0' % f) for f in fields]
    )
