This module bridges ``product_catalog_sale`` with ``sale_rental`` so that
products added from the catalog on a rental order create proper rental lines.

Without this module, the catalog creates regular sale order lines missing
``rental_type``, ``rental_qty`` and dates. This module overrides
``_update_order_line_info`` to automatically set these fields using the
order's default start and end dates.

The catalog quantity represents the number of items to rent (``rental_qty``),
and ``product_uom_qty`` is computed as ``rental_qty × number_of_days``.
