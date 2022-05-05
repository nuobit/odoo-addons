# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# pylint: disable=C7902
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "stock_picking_report_delivery_note",
        "migrations/14.0.1.0.0/noupdate_changes.xml",
    )
