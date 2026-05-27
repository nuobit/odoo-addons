By default, the OCA module ``document_page_reference`` generates a new
reference from a slug of the document title. That is unsuitable for
environments where each document is identified by a fixed-width numeric
code (legacy DMS migrations, ERP integrations, GMP traceability, etc.).

This module replaces the default behavior:

* When a new document page is created without an explicit ``reference``,
  the field is auto-filled from a dedicated ``ir.sequence`` (code
  ``document.page.reference.numeric``) as a zero-padded, 10-digit number.
* When a ``reference`` is provided manually it is left untouched, so
  migrated documents keep their legacy code verbatim.
* Existing document pages keep their current reference.
* Uniqueness is enforced via the existing ``_check_reference`` constraint.

.. note::

   Legacy migration: import the existing documents first (their numeric codes
   are preserved verbatim), then install this module. A post-init hook advances
   the ``document.page.reference.numeric`` sequence above the highest existing
   numeric reference, so auto-generated references never collide with the
   imported ones. (You can also set the sequence's *Next Number* manually.)

.. note::

   A purely numeric reference cannot be used as a ``${...}`` cross-link in a
   page body. ``document_page_reference`` resolves ``${code}`` by treating
   ``code`` as a Jinja variable name, but a pure-digit expression such as
   ``${0000000001}`` is parsed as an integer literal instead of a name, so no
   link is produced. Pages that must be cross-linked need a manual,
   alphanumeric reference.
