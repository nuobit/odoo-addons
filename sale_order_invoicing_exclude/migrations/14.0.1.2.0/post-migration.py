# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # 14.0.1.1.0 reported every excluded order as "Nothing to invoice". Only
    # the ones flagged as "Never invoice" are from now on, so the excluded
    # orders demoted back then have to report "To invoice" again.
    env["sale.order"].search(
        [("sale_invoicing_exclude_from_invoicing", "=", True)]
    )._get_invoice_status()
