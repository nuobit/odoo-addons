- A line with no product, such as a line typed by hand, prints the sample text
  "Bacon Burger" instead of a description.
- The whole description cell is replaced, so what another module adds inside it is
  not printed: for instance, the products of a point of sale down payment that
  `pos_sale` lists there.
- A product variant prints only the name of its product, without its attributes.
- The cell reads the product's current name every time the invoice is printed: an
  invoice printed again after its product is renamed shows the new name.
- The rest of the line's description is not printed: the lines typed into it and
  the product's sales description.
