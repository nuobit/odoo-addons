# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import csv
import logging

from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def _create_fiscal_position_tax_mappings(env, company):
    if not company.chart_template or not company.chart_template.startswith("es_"):
        return
    current_fps = (
        env["account.fiscal.position"]
        .with_context(active_test=False)
        .search(env["account.fiscal.position"]._check_company_domain(company))
    )
    fp_map = {
        xmlid: res_id
        for res_id, xmlid in current_fps.get_external_id().items()
        if xmlid
    }
    current_taxes = (
        env["account.tax"]
        .with_context(active_test=False)
        .search(env["account.tax"]._check_company_domain(company))
    )
    tax_map = {
        xmlid: res_id
        for res_id, xmlid in current_taxes.get_external_id().items()
        if xmlid
    }
    FiscalPositionTax = env["account.fiscal.position.tax"]
    prefix = f"account.{company.id}_"
    with file_open(
        "l10n_es_dua_special_prorrate/data/account_fiscal_position_tax_data.csv"
    ) as csv_file:
        for record in csv.DictReader(csv_file):
            fp_id = fp_map.get(f"{prefix}{record['position_id']}")
            tax_src_id = tax_map.get(f"{prefix}{record['tax_src_id']}")
            tax_dest_id = tax_map.get(f"{prefix}{record['tax_dest_id']}")
            if not fp_id or not tax_src_id or not tax_dest_id:
                continue
            existing = FiscalPositionTax.search(
                [
                    ("position_id", "=", fp_id),
                    ("tax_src_id", "=", tax_src_id),
                    ("tax_dest_id", "=", tax_dest_id),
                ]
            )
            if not existing:
                FiscalPositionTax.create(
                    {
                        "position_id": fp_id,
                        "tax_src_id": tax_src_id,
                        "tax_dest_id": tax_dest_id,
                    }
                )


def post_init_hook(env):
    companies = env["res.company"].search(
        [
            ("chart_template", "like", "es_%"),
        ],
        order="parent_path",
    )
    for company in companies:
        _create_fiscal_position_tax_mappings(env, company)
