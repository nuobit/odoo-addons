This module links the WooCommerce connector with the invoice batches of
``account_invoice_batches``.

The WooCommerce backend gets an **Invoice Batch Sending Method**. The order
import gives it to each new customer and each new invoice address it creates,
each one its own invoice batch contact. An invoice is addressed to its order's
invoice address, so it is sent as that method says: by e-mail to the buyer when
the method is e-mail. Delivery addresses, and the contacts the import finds
already in Odoo, keep their own method.

It is installed by itself when both modules are installed.
