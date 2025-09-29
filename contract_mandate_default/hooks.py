# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions SL 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def post_init_hook(env):
    contracts = env["contract.contract"].search(
        [
            ("payment_mode_id.payment_method_id.mandate_required", "=", True),
            ("mandate_id", "!=", False),
        ]
    )

    for contract in contracts:
        contract.mandate_id = False
