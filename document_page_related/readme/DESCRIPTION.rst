This module adds a *Related Documents* tab to the form of a document (not of
a category), as its last tab. In it, the users who can edit the document add
other documents that complement it, such as a law, a bibliography or another
procedure, and remove them.

Behavior:

* Only documents can be related: never a category, and never the document
  itself.
* The *Open* button of a line opens that document; the breadcrumbs lead back.
* Each user sees only the related documents they can read. The others do not
  appear, and editing the list does not remove them. Archived documents do
  not appear either; they appear again when they are unarchived.
* The list is not part of the history of the document: changing it creates
  no new version and, with *Document Page Approval*, no change request.
* A copy of a document keeps its related documents, except the archived ones
  and those that the user making the copy cannot read. A copy of a related
  document is not related to the documents that list the original.
