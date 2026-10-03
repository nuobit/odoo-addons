This module offers, in the *Procedures* tab of a nonconformity, the documents
stored at any depth under a document category that has a *Management System
Category Type* (module ``mgmtsystem_document_category``), whatever the
categories are called and in whatever language. The categories themselves are
not offered.

It replaces the filter of the OCA ``mgmtsystem_nonconformity`` module, which
offers the documents under the categories named ``Procedure``,
``Environmental Aspect`` or ``Manuals`` in English, and finds nothing in a
tree named in another language.

It is installed automatically when ``mgmtsystem_nonconformity`` and
``mgmtsystem_document_category`` are both installed.
