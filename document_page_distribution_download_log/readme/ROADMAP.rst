* A version saved before the module was installed keeps its original links and
  is not tracked until its content is saved again.
* Uninstalling the module does not restore the original links of the versions
  saved while it was installed: their content keeps the addresses of the
  module, which stop working with it. The links have to be inserted again.
* The address of the file itself (``/web/content``, the one the module
  redirects to) serves the file without any record.
* A download record says that a user opened the address of a file, not that
  the file arrived or was read.
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
