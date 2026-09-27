# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # The job functions are noupdate data: the update leaves the retry
    # pattern of the existing records untouched, so the new values are
    # reloaded here. The update itself creates the new functions.
    openupgrade.load_data(
        env.cr, "connector_woocommerce", "migrations/14.0.0.2.0/noupdate_changes.xml"
    )
    functions = env["queue.job.function"].search(
        [("model_id.model", "=like", "woocommerce.%")], order="name"
    )
    for function in functions:
        _logger.info(
            "Job function %s: channel %s, retry pattern %s",
            function.name,
            function.channel,
            function.retry_pattern,
        )
