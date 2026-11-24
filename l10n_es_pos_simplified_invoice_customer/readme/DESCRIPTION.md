On a Spanish point of sale, `l10n_es_pos` prints the customer's name, tax ID
and address on the ticket of every order that has a customer other than its
generic one, simplified invoices included. A simplified invoice carries the
buyer's tax ID and address only when the buyer is a business or a professional
who asks for them, or needs them for a tax right (Real Decreto 1619/2012,
article 7.2 and 7.3).

With this module, the ticket of a simplified invoice prints the customer only
when the customer has a tax ID. The ticket of an invoice is unchanged.
