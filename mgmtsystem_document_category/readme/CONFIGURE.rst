After installing this module, the nonconformity *Procedures* selection only
offers the documents stored under a document category that has a *Management
System Category Type* set. This replaces the previous name based filter, so
until the categories are classified the selection is empty, also on databases
where that filter used to match (categories named ``Procedure``,
``Environmental Aspect`` or ``Manuals``).

To classify the document categories:

#. Go to *Knowledge > Pages > Categories* (or *Management System >
   Configuration > Categories* when ``mgmtsystem_manual`` is installed).
#. Open each category that holds management system documents.
#. Set its *Management System Category Type* (for example *Procedure*).

The documents stored under a classified category, at any depth, then become
selectable as procedures on the nonconformity.
