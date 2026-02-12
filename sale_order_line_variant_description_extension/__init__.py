from . import models


def _monkey_patch_sale_order_line_description():
    # Import the "bad" class — the one you want to patch
    from odoo.addons.sale_order_line_variant_description.models.sale_order_line import (
        SaleOrderLine as BadSOLine,
    )

    # Define your replacement function
    def _get_sale_order_line_multiline_description_sale(self):
        # just call the next one up in the chain
        return super(BadSOLine, self)._get_sale_order_line_multiline_description_sale()

    # Monkey-patch: replace their method
    BadSOLine._get_sale_order_line_multiline_description_sale = (
        _get_sale_order_line_multiline_description_sale
    )


# Run patch immediately when your module loads
_monkey_patch_sale_order_line_description()
