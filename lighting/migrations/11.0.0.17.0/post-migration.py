# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    env.cr.execute(
        "UPDATE lighting_product p "
        "SET state = 'draft' "
        "WHERE p.in_progress"
    )

    env.cr.execute(
        "UPDATE lighting_product p "
        "SET state = 'discontinued' "
        "WHERE p.discontinued"
    )