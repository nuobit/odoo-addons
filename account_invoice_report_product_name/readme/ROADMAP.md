- A product variant prints only the name of its product, without its attributes.
- The cell reads the product's current name every time the invoice is printed: an
  invoice printed again after its product is renamed shows the new name.
- The rest of the line's label is not printed: the lines typed into it and the
  product's sales description.
- A view that finds the span of the line's label by its options no longer finds it,
  because this module changes them. A module with such a view and this one cannot both
  be installed: the one installed second fails. Odoo refuses such a view created in the
  database later, but does not check one created there before this module is installed
  or updated: printing an invoice then fails.
- A view applied after this module's that replaces the span of the line's label prints
  its own text instead of the product's name. One that replaces the span's options, or
  turns it into a t-out without them, prints the line's label.
- This module's view has priority 1, so that it applies before the report's views of a
  higher priority, Odoo's default of 16 among them. A view with a priority below 1, or
  with 1 and created before it, applies first: a span it puts ahead of the header's span
  prints "Product" instead of its own text, the options it gives the span of the line's
  label give way to this module's, and if it removes that span, this module's view no
  longer finds it.
- A view applied after this module's that replaces Odoo's span of the header prints its
  own text instead of "Product", and what a view adds inside that span does not print,
  because the span prints "Product" instead.
