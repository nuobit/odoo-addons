* Add a per-line ``Selected`` checkbox on sale orders so users can pick
  which lines go into the next regular invoice.
* Persist the selection in the database, so it survives pagination,
  refreshes, and closing the browser.
* Extend the standard *Create Invoice* wizard with an ``Only selected lines``
  option that includes only those flagged lines and resets the flag once
  the invoice is created.
