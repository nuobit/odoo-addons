# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import csv

from odoo.tools import file_open

_TEMPLATE_FILE = (
    "l10n_es_account_capital_asset_tax_map"
    "/data/template/l10n.es.account.capital.asset.map.tax-es_common.csv"
)


def post_init_hook(env):
    companies = (
        env["res.company"]
        .search([])
        .filtered(lambda c: c.chart_template and c.chart_template.startswith("es_"))
    )
    if not companies:
        return
    with file_open(_TEMPLATE_FILE) as template_file:
        records = list(csv.DictReader(template_file))
    for company in companies:
        existing = env["l10n.es.account.capital.asset.map.tax"].search_count(
            [("company_id", "=", company.id)]
        )
        if existing:
            continue
        for record in records:
            tax_src = env.ref(
                f"account.{company.id}_{record['tax_src_id']}",
                raise_if_not_found=False,
            )
            tax_dest = env.ref(
                f"account.{company.id}_{record['tax_dest_id']}",
                raise_if_not_found=False,
            )
            if not tax_src or not tax_dest:
                continue
            env["l10n.es.account.capital.asset.map.tax"].create(
                {
                    "company_id": company.id,
                    "tax_src_id": tax_src.id,
                    "tax_dest_id": tax_dest.id,
                }
            )
