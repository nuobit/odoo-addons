# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        quants = super()._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        # Adjust reservation to be first FIFO/FEFO and then use location name
        # alphabetically
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        if removal_strategy == "fifo":
            quants = quants.sorted(lambda q: (q.in_date, q.location_id.name))
        elif removal_strategy == "fefo":
            quants = quants.sorted(
                lambda q: (q.removal_date, q.in_date, q.location_id.name)
            )
        elif removal_strategy == "lifo":
            # sorting 2 keys and only one of them reversed it is a bit tricky,
            # Oxigen does not use this method at the moment, therefore it is
            # not worth implementing.
            pass
        return quants
