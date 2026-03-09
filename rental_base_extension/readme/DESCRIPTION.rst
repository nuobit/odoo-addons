This module extends ``rental_base`` to improve the rental order experience
with better menu visibility and product filtering.

Rental Positions menu
~~~~~~~~~~~~~~~~~~~~~

The ``rental_base`` module places the Rental Positions screen (the ``sale.rental``
list) under Configuration and restricts it to debug mode. This module moves it
to the top level of the Rentals menu as the first entry, visible to all sales
users, since it is the primary screen for tracking rental status.

Product filter on rental order lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a rental order, the product dropdown on order lines only shows
rental service products (i.e. products linked to a rented physical product
via ``rented_product_id``). This prevents users from accidentally selecting
non-rental products on rental orders.

Catalan and Spanish translations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides Catalan and Spanish translations for ``rental_base``, which does not
ship with these languages.
