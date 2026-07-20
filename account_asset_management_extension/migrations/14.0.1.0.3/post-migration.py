# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # `quantity` was introduced as required without backfilling existing
    # assets, so pre-2023 rows kept NULL and the NOT NULL constraint never
    # installs. Assets linked to an invoice line must take the line quantity
    # (the _check_invoice constraint enforces equality on write); a line
    # quantity of NULL/0 is unusable (_check_quantity_on_asset forbids 0).
    cr.execute(
        """
        UPDATE account_asset a
        SET quantity = l.quantity
        FROM account_move_line l
        WHERE l.id = a.invoice_move_line_id
          AND a.quantity IS NULL
          AND l.quantity IS NOT NULL
          AND l.quantity != 0
        """
    )
    _logger.info(
        "account_asset.quantity backfilled from linked invoice line: %s rows",
        cr.rowcount,
    )
    cr.execute("UPDATE account_asset SET quantity = 1 WHERE quantity IS NULL")
    _logger.info(
        "account_asset.quantity defaulted to 1 (no usable invoice line): %s rows",
        cr.rowcount,
    )
