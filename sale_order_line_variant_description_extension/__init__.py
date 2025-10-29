from . import models


def _monkey_patch_product_id_change():
    # Import the "bad" class — the one you want to patch
    from odoo.addons.sale_order_line_variant_description.models.sale_order_line import (
        SaleOrderLine as BadSOLine,
    )

    from odoo import api

    # Define your replacement function
    @api.onchange("product_id")
    def product_id_change(self):
        # just call the next one up in the chain
        return super(BadSOLine, self).product_id_change()

    # Monkey-patch: replace their method
    BadSOLine.product_id_change = product_id_change


# Run patch immediately when your module loads
_monkey_patch_product_id_change()
