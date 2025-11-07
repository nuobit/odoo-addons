# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import csv

from odoo.tools import file_open


def post_init_hook(env):
    companies = env.companies.filtered(
        lambda company: company.chart_template
        and company.chart_template.startswith("es_")
    )

    current_tax_groups = env["account.tax.group"].search([])

    external_id_map = current_tax_groups.get_external_id()
    tax_group_map = {
        external_id: env["account.tax.group"].browse(tax_group_id)
        for tax_group_id, external_id in external_id_map.items()
    }

    with file_open(
        "l10n_es_extension/data/template/account.tax.group-es_common_mainland.csv"
    ) as template_file:
        for record in csv.DictReader(template_file):
            for company in companies:
                ext = "account.{}_{}".format(company.id, record["id"])
                tax_group = tax_group_map.get(ext)
                if tax_group:
                    tax_group.write({"is_vat": record["is_vat"]})
