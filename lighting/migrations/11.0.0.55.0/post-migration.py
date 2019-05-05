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

    _logger.info("Populating 'Is composite' field from required_ids...")

    products = env['lighting.product'].search([('required_ids', '!=', False)])
    n = len(products)
    th = int(n / 100) or 1
    for i, p in enumerate(products, 1):
        p.is_composite = True
        if (i % th) == 0:
            _logger.info(" - Progress populating 'Is composite' %i%%" % (int(i / n * 100)))

    _logger.info("'Is composite' field successfully populated from required_ids")
