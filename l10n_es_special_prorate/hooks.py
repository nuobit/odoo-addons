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
        .with_context(
            active_test=False,
        )
        .search(env["account.fiscal.position"]._check_company_domain(company))
    )
    fp_map = {
        xmlid: res_id
        for res_id, xmlid in current_fps.get_external_id().items()
        if xmlid
    }
    current_taxes = (
        env["account.tax"]
        .with_context(
            active_test=False,
        )
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
        "l10n_es_special_prorate/data/account_fiscal_position_tax_data.csv"
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
                ],
                limit=1,
            )
            if not existing:
                FiscalPositionTax.create(
                    {
                        "position_id": fp_id,
                        "tax_src_id": tax_src_id,
                        "tax_dest_id": tax_dest_id,
                    }
                )


def _get_prorate_tax_data(chart_template):
    tax_data = chart_template._parse_csv(
        "es_common_mainland",
        "account.tax",
        module="l10n_es_special_prorate",
    )
    chart_template._deref_account_tags("es_pymes", tax_data)
    return tax_data


def post_init_hook(env):
    companies = env["res.company"].search(
        [
            ("chart_template", "like", "es_%"),
        ],
        order="parent_path",
    )
    for company in companies:
        ChartTemplate = env["account.chart.template"].with_company(company)
        tax_data = _get_prorate_tax_data(ChartTemplate)
        # Skip taxes that already exist to avoid duplicating repartition lines
        for xmlid in list(tax_data):
            if ChartTemplate.ref(xmlid, raise_if_not_found=False):
                del tax_data[xmlid]
        if tax_data:
            ChartTemplate._load_data({"account.tax": tax_data})
        _create_fiscal_position_tax_mappings(env, company)
