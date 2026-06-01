When checkout login is mandatory, Odoo redirects anonymous visitors from
``/shop/checkout`` directly to ``/web/login``.

This module keeps the checkout requirement intact, but first sends those
visitors back to ``/shop/cart`` so they can review the order and use the
standard cart sign-in call to action.
