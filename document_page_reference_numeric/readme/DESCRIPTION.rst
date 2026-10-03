The OCA module ``document_page_reference`` proposes, for a document created
without a reference, one made from its title. This module gives it a number
instead:

* A document created without a reference gets the next number of the sequence
  with code ``document.page.reference.numeric``, which the module creates
  zero-padded to 10 digits. If no active sequence has that code, such a
  document cannot be saved until a reference is typed.
* A reference typed by hand, such as a code from a previous system, is kept as
  typed and does not move the sequence.
* A number already used as the reference of another document, of any company,
  archived or not, is skipped: the document gets the next free one.
* A duplicated document gets a new number.
* A document cannot be saved without a reference: clearing the reference of a
  saved document is refused.
* Categories are documents and follow the same rules.
