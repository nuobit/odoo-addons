# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # recalculate total wattages
    _logger.info("Recalculating total wattages...")

    products = env['lighting.product'].search([('total_wattage_auto', '=', True)])
    n = len(products)
    th = int(n / 100) or 1
    for i, p in enumerate(products, 1):
        p._compute_total_wattage()
        if (i % th) == 0:
            _logger.info(" - Progress Recalculating total wattages %i%%" % (int(i / n * 100)))

    _logger.info("Total wattages successfully recalculated")
