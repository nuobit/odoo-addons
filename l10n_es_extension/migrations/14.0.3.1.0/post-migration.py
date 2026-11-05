# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Materialized taxes carrying the l10n_es template xml-id p_iva4_sp_ex,
# any company prefix, any owning module.
_XMLID_RE = re.compile(r"^\d+_account_tax_template_p_iva4_sp_ex$")
_TEMPLATE_ORDER = "base:100|tax:-100|tax:100"


def _order_sig(lines):
    """Return the "type:factor|..." signature in (sequence, id) order."""
    ordered = lines.sorted(key=lambda r: (r.sequence, r.id))
    return "|".join(
        "%s:%d" % (r.repartition_type, int(r.factor_percent)) for r in ordered
    )


def migrate(cr, version):
    """Re-align p_iva4_sp_ex repartition-line ORDER with the l10n_es template.

    Where a company holds this tax with its two TAX repartition lines in
    the REVERSE order of the l10n_es template, the order-sensitive core
    update_taxes_from_templates check judges the tax "different" at the
    next major-version hop, strips its xml-id and forks it into
    "[old] ..." + a duplicate. Setting sequence=2 on the +100% TAX line
    restores the (sequence, id) order to base|-100|+100 so the tax stays
    template-managed. Pure ordering field: no amounts, accounts, tags, or
    rows touched. Idempotent; tolerant of installs without this tax.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    imds = env["ir.model.data"].search(
        [
            ("model", "=", "account.tax"),
            ("name", "=like", "%_account_tax_template_p_iva4_sp_ex"),
        ]
    )
    taxes = (
        env["account.tax"]
        .browse(imds.filtered(lambda d: _XMLID_RE.match(d.name)).mapped("res_id"))
        .exists()
    )
    if not taxes:
        _logger.info("p_iva4_sp_ex reorder: not present on this database, skipping")
        return
    lines = env["account.tax.repartition.line"].search(
        [
            "|",
            ("invoice_tax_id", "in", taxes.ids),
            ("refund_tax_id", "in", taxes.ids),
            ("repartition_type", "=", "tax"),
            ("factor_percent", "=", 100),
            ("sequence", "!=", 2),
        ]
    )
    for tax in taxes:
        _logger.info(
            "p_iva4_sp_ex reorder: tax %s (company %s) BEFORE "
            "invoice=[%s] refund=[%s]",
            tax.id,
            tax.company_id.id,
            _order_sig(tax.invoice_repartition_line_ids),
            _order_sig(tax.refund_repartition_line_ids),
        )
    lines.write({"sequence": 2})
    bad = taxes.filtered(
        lambda t: _order_sig(t.invoice_repartition_line_ids) != _TEMPLATE_ORDER
        or _order_sig(t.refund_repartition_line_ids) != _TEMPLATE_ORDER
    )
    if bad:
        raise RuntimeError(
            "l10n_es_extension 14.0.3.1.0: %d p_iva4_sp_ex tax(es) still not "
            "in template order (%s) after reorder: %s"
            % (len(bad), _TEMPLATE_ORDER, bad.ids)
        )
    _logger.info(
        "p_iva4_sp_ex reorder OK: %d tax(es) in template order (%s)",
        len(taxes),
        _TEMPLATE_ORDER,
    )
