* A version saved before the module was installed keeps its original links and
  is not tracked until its content is saved again.
* Uninstalling the module does not restore the original links of the versions
  saved while it was installed: their content keeps the addresses of the
  module, which stop working with it. The links have to be inserted again.
* The file's own address serves it without any record: the module redirects to
  it (``/web/content``), the attachment box of the document's chatter offers it
  with a download icon, and its image address (``/web/image``) serves it too.
* A download record says that the user's browser asked for the file to hand it
  to the user, not that the file arrived or was read. The module tells that
  request from the others by what the browser declares: the ``Sec-Fetch-Dest``
  header, and ``Sec-Purpose`` and the older prefetch headers. A browser that
  declares nothing, such as an older browser or any browser on a site served
  over plain HTTP other than localhost, and a program are recorded on every
  request.
* An address loaded by a frame of a page (``iframe``, ``frame``, ``embed`` or
  ``object``) is recorded as a download: the browser receives the file, and a
  link clicked inside a frame asks for it the same way. Odoo removes these
  elements from the content of documents and from messages.
* A program or a download manager that asks for the address several times, to
  resume a download for instance, writes one record per request.
* A file with a recorded download stays: it cannot be deleted, and Odoo has no
  archive for files. A wrong file is corrected with a new version of the
  document that links the right one; removing a file once downloaded needs a
  technician. A record that owns such a file cannot be deleted either, since
  Odoo deletes a record's attachments with it, for instance a document whose
  file another document links: archive it instead.
* A download of a user who is not a recipient of the version is recorded and
  shown in no list of the module; it counts as soon as the version is
  distributed to that user.
* Every version differs from the previous one by the addresses of its links,
  which carry the version: the comparison of two versions always shows the
  lines of the links as changed.
