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

    env.cr.execute(
        """update lighting_product p
           set is_composite = TRUE
           where exists (
                    select 1
                    from lighting_product_required_rel r
                    where r.product_id = p.id
                 )
        """)

    _logger.info("'Is composite' field successfully populated from required_ids")
