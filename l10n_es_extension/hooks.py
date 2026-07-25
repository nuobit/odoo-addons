# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import csv

from odoo.tools import file_open


def _get_nd_tax_data(chart_template):
    tax_data = chart_template._parse_csv(
        "es_common_mainland",
        "account.tax",
        module="l10n_es_extension",
    )
    # _deref_account_tags only uses the code to resolve the chart's country,
    # and it must be an installable chart code (es_common_mainland is just a
    # shared data-file suffix, not a chart).
    chart_template._deref_account_tags("es_pymes", tax_data)
    return tax_data


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
        "l10n_es_extension/data/account_fiscal_position_tax_data.csv"
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

    nd_companies = env["res.company"].search(
        [
            ("chart_template", "like", "es_%"),
        ],
        order="parent_path",
    )
    for company in nd_companies:
        ChartTemplate = env["account.chart.template"].with_company(company)
        tax_data = _get_nd_tax_data(ChartTemplate)
        # Skip taxes that already exist to avoid duplicating repartition lines
        # (on databases migrated from previous versions the whole family is
        # already instantiated under the account.<company>_<template> xml-ids).
        for xmlid in list(tax_data):
            if ChartTemplate.ref(xmlid, raise_if_not_found=False):
                del tax_data[xmlid]
        if tax_data:
            ChartTemplate._load_data({"account.tax": tax_data})
        _create_fiscal_position_tax_mappings(env, company)
