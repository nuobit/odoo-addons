This module extends ``rental_base`` to provide a complete rental order
management experience.

Dedicated rental views
~~~~~~~~~~~~~~~~~~~~~~

Replaces the default sale order views with dedicated rental-specific views:
form, tree, kanban, calendar and search. The form view hides non-rental fields
and adds rental period, duration and status badges. Actions set the rental sale
type by default.

Rental status tracking
~~~~~~~~~~~~~~~~~~~~~~

Adds computed ``rental_status`` on sale orders based on the state of the
underlying ``sale.rental`` records: draft, pickup, return, returned and cancel.
A "late" indicator warns when the next action date has passed.

Rental Positions menu
~~~~~~~~~~~~~~~~~~~~~

The ``rental_base`` module places the Rental Positions screen under
Configuration and restricts it to debug mode. This module moves it to the
top level of the Rentals menu as the first entry, visible to all sales users.

Product filter on rental order lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a rental order, the product dropdown only shows rental service
products, preventing users from accidentally selecting non-rental products.

Signature and delivery
~~~~~~~~~~~~~~~~~~~~~~

Configurable signature terms for rental delivery orders (Settings → Rental →
Signature). When enabled, the Validate button is replaced by a Sign button
that auto-validates on signature. The signed conditions appear on the delivery
slip PDF.

Catalan and Spanish translations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides Catalan and Spanish translations for ``rental_base``, which does not
ship with these languages.
