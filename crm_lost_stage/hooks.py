# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)


def migrate_existing_lost_leads(env):
    _logger.info("Start: Migrating CRM leads by setting the lost stage.")

    leads = env["crm.lead"].search([("active", "=", False)])
    for lead in leads:
        lead.action_set_lost()

    _logger.info(
        f"End: Successfully migrated {len(leads)} CRM leads to the lost stage."
    )
