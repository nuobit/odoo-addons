This module records who downloaded the files of a distributed document: it is
the download log of *Document Page Distribution*. That module sends a version of
a document to its readers and keeps the log of the sends; this one keeps, for
every version, the evidence that a reader downloaded a file linked in its
content.

When a version of a document is saved, every link of its content that points to
an attachment is rewritten to an address of this module that carries the
version and the file. When the user's browser asks for that address to hand the
file to the user, the module checks that the user can read the document,
records the download and serves the file as Odoo does. When the browser says
that it asks for it as a part of another page, such as an image in a message,
or ahead of the user, such as a prefetch, the module answers *not found* and
records nothing. A browser that says nothing is served and recorded.

A download is recorded for every user who downloads a file, whether or not the
version was distributed to that user. When the user is a recipient of the
version, the recipient line shows the downloads: whether the user downloaded,
how many times, the first and the last date. Every version says in *Downloads*
how many of its recipients downloaded at least one of its files: *3/10* means 3
of 10.

No user can create, edit or delete a download record. A version or a document
with recorded downloads cannot be deleted, only archived. A file with a
recorded download cannot be deleted either, by anyone: the user who downloaded
it holds a copy, and the record keeps saying which file it was. Neither can a
record that owns such a file, such as another document: Odoo deletes a record's
files with it, so archive the record instead. A download record says that the
user's browser asked for the file to hand it to the user: a click on the link,
the link opened in a new tab, a save of the link. The log cannot know whether
the file arrived or was read.

Visibility follows the security groups of the document: a user sees the
downloads of the documents they can read, and a document manager sees all of
them.
