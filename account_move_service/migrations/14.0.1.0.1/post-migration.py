# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    service_moves = env["account.move"].search(
        [("partner_id.service_intermediary", "=", True)],
    )
    products = env["product.product"]
    for company in service_moves.company_id:
        products |= service_moves.get_config_service_group_product(company)
    service_move_line = env["account.move.line"]
    for prod in products:
        service_move_line |= service_moves.line_ids.filtered(
            lambda x: x.product_id == prod
        )
    service_move_line.service_group = True
