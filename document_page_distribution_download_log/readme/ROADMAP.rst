* A version saved before the module was installed keeps its original links and
  is not tracked until its content is saved again.
* Uninstalling the module does not restore the original links of the versions
  saved while it was installed: their content keeps the addresses of the
  module, which stop working with it. The links have to be inserted again.
* The address of the file itself (``/web/content``, the one the module
  redirects to) serves the file without any record.
* A download record says that a user opened the address of a file, not that
  the file arrived or was read.
* A download of a user who is not a recipient of the version is recorded and
  shown in no list of the module; it counts as soon as the version is
  distributed to that user.
* Every version differs from the previous one by the addresses of its links,
  which carry the version: the comparison of two versions always shows the
  lines of the links as changed.
