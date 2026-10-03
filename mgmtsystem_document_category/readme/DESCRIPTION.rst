This module classifies the document categories for the management system, so
that the management system finds its documents whatever the categories are
called and in whatever language.

* A document category gets a *Management System Category Type*: ``Procedure``,
  ``Environmental Aspect``, ``Quality Manual`` or ``Environment Manual``. Only
  a category can have one.
* A document gets the searchable flag *Management System Document* when it is
  stored, at any depth, under a category that has a type. A category never
  has the flag.

The glue modules ``mgmtsystem_nonconformity_document_category`` and
``mgmtsystem_audit_document_category`` use the flag to offer these documents
as the procedures of nonconformities and audits; each one is installed
automatically with the module it extends.
