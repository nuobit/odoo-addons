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

    env.cr.execute(
        "insert into lighting_product_optional_rel(product_id, optional_id) "
        "select product_id, accessory_id "
        "from lighting_product_accessory_rel"
    )

    _logger.info("Accessory data successfully copied to Optional")
