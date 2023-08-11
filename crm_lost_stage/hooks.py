# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate_existing_lost_leads(cr, registry):
    _logger.info("Start: Migrating CRM leads by setting the lost stage.")

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        leads = env["crm.lead"].search([("active", "=", False)])
        for lead in leads:
            lead.action_set_lost()

    _logger.info(
        "End: Successfully migrated %s CRM leads to the lost stage." % len(leads)
    )
