After installing this module, the audit verification line *Procedure* selection
only offers the documents stored directly under a document category that has a
*Management System Category Type* set. This replaces the previous name based
filter, so until the categories are classified the selection is empty, also on
databases where that filter used to match (categories named ``Procedure``,
``Environmental Aspect``, ``Quality Manual`` or ``Environment Manual``).

The classification is the same one used by the nonconformity *Procedures*
selection (provided by ``mgmtsystem_document_category``): categories already
classified for the nonconformity are picked up by the audit immediately.

To classify the document categories:

#. Go to *Knowledge > Pages > Categories* (or *Management System >
   Configuration > Categories* when ``mgmtsystem_manual`` is installed).
#. Open each category that holds management system documents.
#. Set its *Management System Category Type* (for example *Procedure*).

The documents stored directly under a classified category then become
selectable as procedures on the audit verification lines.
