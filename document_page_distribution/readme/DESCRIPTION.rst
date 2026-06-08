This module adds a *Distribute* action on document pages. When a document
manager distributes a page, its current version is emailed to every
user that has read access to the document according to its configured security
groups, and an auditable distribution log is kept (who distributed which
version, when, and to whom).

The distributed version is the document's current version. If the document has
no current version yet, distribution is blocked. When *Document Page Approval*
is installed, the current version is the latest approved one, so only approved
content is distributed.

Distributing the same version again resends the email as a reminder without
creating a new document version.
