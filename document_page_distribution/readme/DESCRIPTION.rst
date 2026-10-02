This module adds a *Distribute* action on document pages. A document manager
sends the current version of a document by email to its readers, and the module
keeps a distribution log per version: who distributed it, when, to whom, and
the delivery status of the email of every recipient.

In this module, distributed means notified by email, with the delivery status
of every recipient.

The users in scope of a distribution are the active internal users that belong
to any of the groups set in the *Security* tab of the document and, when the
document has a company, to that company. Every user in scope gets a line in
the log of the version. The email goes only to the users that can read the
document and have an email address; the others stay in the log with the state
*No access* or *No email*.

The distributed version is the document's current version. If the document has
no current version yet, distribution is blocked. When *Document Page Approval*
is installed, the current version is the latest approved one, so only approved
content is distributed.

Distributing the same version again resends the email as a reminder without
creating a new document version.

No user can edit or delete the log. A document with a log cannot be deleted,
only archived, and a version with a log cannot be deleted.
