* On a new document, files added on its *Editables* tab before a category that
  requires approval is chosen are not saved: the tab turns read-only and the
  screen leaves them out of the save, with no warning. Through the API, such a
  document is refused with its files. Where a document requires approval, its
  files change in a draft change request.
* Uninstalling ``document_page_approval`` deletes its change requests in draft,
  pending approval or cancelled, and this module deletes their editable files
  first. Uninstalled alone before it, this module does not: the attachments that
  hold the contents of those files then stay once ``document_page_approval``
  goes, until ``document_page_editable_file`` is uninstalled.
