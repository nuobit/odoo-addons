# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    openupgrade.date_to_datetime_tz(
        env.cr,
        "sale_order",
        "create_uid",
        openupgrade.get_legacy_name("service_date"),
        "service_date",
    )
