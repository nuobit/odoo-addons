Shared base of the NuoBiT modules of the Knowledge application
(``document_page_*``): what those modules have in common is written once, here.

It holds the protection of the files of a document:

* The HTML editor puts an access token in the link of every file it inserts in
  a document, and Odoo serves a file with a valid token to anyone who has the
  link, without checking any permission and even without a session.
* With this module, a file of a document goes only to whoever can read the
  document, with the token or without it. Anyone else gets *Not found*, as for
  any file Odoo does not serve.
* The same holds for a file of a version of the document, such as one inserted
  in a change request.
* A file kept in a field of the document that is restricted to some groups goes
  only to whoever can read that field as well.
* A file of a document not saved yet goes only to its uploader and the system
  administrators, as Odoo does with any file of no record.
* A file inserted in a version before its first save becomes a file of the
  version when the version is saved, so the readers of the document get it too.
