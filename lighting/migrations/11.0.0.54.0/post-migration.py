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

    _logger.info("Copying Accessory data to Optional...")

    products = env['lighting.product'].search([('accessory_ids', '!=', False)])
    n = len(products)
    th = int(n / 100) or 1
    for i, p in enumerate(products, 1):
        p.optional_ids = [(6, False, p.accessory_ids.mapped('id'))]
        if (i % th) == 0:
            _logger.info(" - Progress moving accessory data %i%%" % (int(i / n * 100)))

    _logger.info("Accessory data successfully copied to Optional")
