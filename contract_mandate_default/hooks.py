# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    contracts = env["contract.contract"].search(
        [
            ("payment_mode_id.payment_method_id.mandate_required", "=", True),
            ("mandate_id", "!=", False),
        ]
    )

    for contract in contracts:
        contract.mandate_id = False
