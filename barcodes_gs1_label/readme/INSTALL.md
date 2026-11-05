After migrating a database from 17.0, check two options on each label
configuration (*Inventory > Configuration > Barcode Labels > Configurations*):

- *Show weight* is new, and it starts unticked. On 17.0, GS1 labels printed
  their weight whenever they had one in kg, with no option: tick it where the
  labels must keep showing the weight.
- *Show currency* now acts on EAN13 labels, which print the price without its
  currency while it is unticked. On 17.0 the form never showed it, and every
  price was printed with its currency: tick it on the EAN13 configurations
  whose labels must keep showing the currency.
