* Uninstalling ``document_page_approval`` deletes its change requests that are
  not approved, and this module deletes their editable files first. Uninstalled
  alone before it, this module does not: the attachments that hold the contents
  of those files then stay once ``document_page_approval`` goes, until
  ``document_page_editable_file`` is uninstalled.
