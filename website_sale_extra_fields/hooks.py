# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info(
        "Pre-creating slug_name column on product_public_category"
        " to avoid NOT NULL constraint failure"
    )
    cr.execute(
        "ALTER TABLE product_public_category"
        " ADD COLUMN IF NOT EXISTS slug_name varchar"
    )
    cr.execute(
        "UPDATE product_public_category SET slug_name = '/' WHERE slug_name IS NULL"
    )
