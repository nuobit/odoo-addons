# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    fields = [
        ('novelty', 'N'),
        ('cataloged', 'C'),
        ('discontinued_by_supplier', 'DS'),
        ('until_end_stock', 'ES'),
        ('discontinued', 'D'),
    ]

    for f, v in fields:
        env.cr.execute(
            "UPDATE lighting_product "
            "SET state_marketing=%%s "
            "WHERE coalesce(%s, false)" % f, (v,))
