# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    normal_type = env.ref("sale_order_type.normal_sale_type")
    cr.execute(
        "UPDATE sale_order SET type_id = %s WHERE type_id IS NULL",
        [normal_type.id],
    )
    _logger.info("Updated %d sale orders with default type_id", cr.rowcount)
    cr.execute("UPDATE sale_order_line SET rental = False WHERE rental IS NULL")
    _logger.info("Updated %d sale order lines with rental = False", cr.rowcount)
    cr.execute(
        "UPDATE sale_order_line SET can_sell_rental = False WHERE can_sell_rental IS NULL"
    )
    _logger.info(
        "Updated %d sale order lines with can_sell_rental = False", cr.rowcount
    )
