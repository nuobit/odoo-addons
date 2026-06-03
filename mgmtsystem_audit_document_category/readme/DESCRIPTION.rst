This module makes the management system audit **Procedure** selection robust
against the document category name and language.

The OCA ``mgmtsystem_audit`` module filters the *Procedure* field of an audit
verification line by matching hardcoded English category names (``Procedure``,
``Environmental Aspect``, ``Quality Manual``, ``Environment Manual``). That match
relies on the category title, so it breaks as soon as the categories are renamed
or created in another language (for example in Spanish), leaving the field empty
even though procedures exist.

This module replaces that name based match with the explicit *Management System
Category Type* classification provided by ``mgmtsystem_document_category``:

* The verification line *Procedure* field, both in the form and in the search
  filter, offers every document stored directly under a classified category,
  resolved from that stable classification instead of from the category name.

As a result the selection keeps working regardless of how the categories are
named or in which language they are used.
