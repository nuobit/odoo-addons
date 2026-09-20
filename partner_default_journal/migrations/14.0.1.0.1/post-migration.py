# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# pylint: disable=C7902

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("partner_default_journal: moving column values to ir.property")

    env.cr.execute(
        """
        SELECT p.id, p.sale_journal_id, j.company_id
        FROM res_partner p
        JOIN account_journal j ON p.sale_journal_id = j.id
        WHERE p.sale_journal_id IS NOT NULL
        """
    )
    _migrate_column(env, "sale_journal_id", env.cr.fetchall())

    env.cr.execute(
        """
        SELECT p.id, p.purchase_journal_id, j.company_id
        FROM res_partner p
        JOIN account_journal j ON p.purchase_journal_id = j.id
        WHERE p.purchase_journal_id IS NOT NULL
        """
    )
    _migrate_column(env, "purchase_journal_id", env.cr.fetchall())

    # Drop the now-orphan columns. Odoo doesn't auto-drop them when a field
    # changes from stored to company_dependent.
    env.cr.execute(
        """
        ALTER TABLE res_partner
        DROP COLUMN IF EXISTS sale_journal_id,
        DROP COLUMN IF EXISTS purchase_journal_id
        """
    )
    _logger.info("partner_default_journal: dropped legacy columns from res_partner")


def _migrate_column(env, field, rows):
    if not rows:
        _logger.info("partner_default_journal: no values to migrate for %s", field)
        return

    for partner_id, journal_id, company_id in rows:
        env["res.partner"].with_company(company_id).browse(partner_id).write(
            {field: journal_id}
        )

    _logger.info(
        "partner_default_journal: migrated %s for %d partner(s)",
        field,
        len(rows),
    )
