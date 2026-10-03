* The module numbers documents when they are created: a document that already
  exists without a reference when the module is installed keeps none until a
  reference is typed on it.
* A reference cannot be cleared, so the test ``test_no_contrains`` of
  ``document_page_reference``, which clears two references, fails when it runs
  on a database where this module is installed.
* A reference made only of digits cannot be used as a ``${...}`` cross-link in
  the body of a page: ``document_page_reference`` reads ``${code}`` as the name
  of a variable, and ``${0000000001}`` is read as a number instead, so no link
  is made. A page that must be the target of a cross-link needs a reference
  typed by hand that starts with a letter or an underscore.
