# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MODULE = "l10n_es_extension"


def _company_record(env, company, template, model):
    """Resolve the company record instantiated from ``template``.

    The chart wizard stamps company records with the xml-id
    ``<template_module>.<company_id>_<template_name>``, but during a
    module handover the custody of an existing record may still sit
    under the previous module, so the lookup matches by terminal name
    only. More than one match means two modules claim the same
    terminal name for the same company: that is never legitimate, so
    fail loudly instead of guessing.
    """
    xmlid = template.get_external_id().get(template.id)
    if not xmlid:
        return None
    name = "%s_%s" % (company.id, xmlid.split(".", 1)[1])
    imds = env["ir.model.data"].search([("model", "=", model), ("name", "=", name)])
    if len(imds) > 1:
        raise RuntimeError(
            "fptt materialization: ambiguous company record for %s (company %s):"
            " modules %s" % (xmlid, company.id, imds.mapped("module"))
        )
    return env[model].browse(imds.res_id) if imds else None


def migrate(cr, version):
    """Materialize this module's fiscal position lines on existing companies.

    Template mapping lines only flow to companies through the chart
    wizard, so the lines added by this version (and any line of this
    module a company is missing) must be created explicitly on the
    fiscal positions that already exist. Companies or taxes not
    instantiated are skipped with a log line: completing a partial
    chart is the wizard's job, not this migration's.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    imd_model = env["ir.model.data"]
    line_model = env["account.fiscal.position.tax"]
    tmpl_imds = imd_model.search(
        [
            ("module", "=", MODULE),
            ("model", "=", "account.fiscal.position.tax.template"),
        ]
    )
    companies = env["res.company"].search([])
    for imd in tmpl_imds:
        tmpl = env["account.fiscal.position.tax.template"].browse(imd.res_id).exists()
        if not tmpl:
            continue
        for company in companies:
            position = _company_record(
                env, company, tmpl.position_id, "account.fiscal.position"
            )
            if not position:
                continue
            src = _company_record(env, company, tmpl.tax_src_id, "account.tax")
            if not src:
                _logger.info(
                    "fptt materialization: company %s has no tax for %s, skipping"
                    " %s (complete the chart with the update wizard if needed)",
                    company.id,
                    tmpl.tax_src_id.name,
                    imd.name,
                )
                continue
            dest = None
            if tmpl.tax_dest_id:
                dest = _company_record(env, company, tmpl.tax_dest_id, "account.tax")
                if not dest:
                    _logger.info(
                        "fptt materialization: company %s has no tax for %s,"
                        " skipping %s",
                        company.id,
                        tmpl.tax_dest_id.name,
                        imd.name,
                    )
                    continue
            if line_model.search_count(
                [
                    ("position_id", "=", position.id),
                    ("tax_src_id", "=", src.id),
                    ("tax_dest_id", "=", dest.id if dest else False),
                ]
            ):
                continue
            line_name = "%s_%s" % (company.id, imd.name)
            if imd_model.search_count(
                [
                    ("model", "=", "account.fiscal.position.tax"),
                    ("name", "=", line_name),
                ]
            ):
                continue
            line = line_model.create(
                {
                    "position_id": position.id,
                    "tax_src_id": src.id,
                    "tax_dest_id": dest.id if dest else False,
                }
            )
            imd_model.create(
                {
                    "module": MODULE,
                    "name": line_name,
                    "model": "account.fiscal.position.tax",
                    "res_id": line.id,
                    "noupdate": True,
                }
            )
            _logger.info(
                "fptt materialization: created %s.%s on position %s (company %s)",
                MODULE,
                line_name,
                position.name,
                company.id,
            )
