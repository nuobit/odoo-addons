This module makes the management system **Procedures** selection robust against
the document category name and language.

The OCA ``mgmtsystem_nonconformity`` module filters the *Procedures* field of a
nonconformity by matching hardcoded English category names (``Procedure``,
``Environmental Aspect``, ``Manuals``). That match relies on the category title,
so it breaks as soon as the categories are renamed or created in another
language (for example in Spanish), leaving the field empty even though
procedures exist.

This module replaces that name based match with an explicit classification:

* It adds a *Management System Category Type* selection on document categories
  (``Procedure``, ``Environmental Aspect``, ``Quality Manual``,
  ``Environment Manual``).
* The nonconformity *Procedures* field then offers every document stored under a
  classified category (at any depth), resolved from that stable classification
  instead of from the category name.

As a result the selection keeps working regardless of how the categories are
named or in which language they are used.
