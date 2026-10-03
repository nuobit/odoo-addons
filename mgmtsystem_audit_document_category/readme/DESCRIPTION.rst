This module offers, as the *Procedure* of an audit verification line, in the
form and in the search, the documents stored at any depth under a document
category that has a *Management System Category Type* (module
``mgmtsystem_document_category``), whatever the categories are called and in
whatever language. The categories themselves are not offered.

It replaces the filter of the OCA ``mgmtsystem_audit`` module, which offers the
documents stored directly under the categories named ``Procedure``,
``Environmental Aspect``, ``Quality Manual`` or ``Environment Manual`` in
English, and finds nothing in a tree named in another language.

It is installed automatically when ``mgmtsystem_audit`` and
``mgmtsystem_document_category`` are both installed.
