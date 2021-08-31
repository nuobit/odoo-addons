# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        UPDATE stock_putaway_rule spr
        SET exclude_internal_operations = pp.exclude_internal_operations
        FROM product_putaway pp
        WHERE spr.putaway_id = pp.id
        """
    )
