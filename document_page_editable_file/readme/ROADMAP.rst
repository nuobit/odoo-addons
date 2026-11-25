* ``document_page_access_group`` limits who reads a document, not who reads its
  versions: a Knowledge editor outside the groups of a document's *Security*
  tab still reads and changes the editable files of its versions.
* Through the API, a write that moves an editable file into a version of another
  company and sets its file in the same call, with ``bin_size`` in its context,
  is not refused: Odoo serves the file from its cache to the check that refuses
  such a move. The screens never send such a call.
* The information inside a file, such as the author, the tracked changes or the
  comments of a Word file, is not cleaned.
* Uninstalling the module deletes every editable file: Odoo deletes the
  attachments of the models it removes.
* Deleting a company deletes its documents, their versions and their editable
  files, but not the attachments that hold the files' contents, as Odoo leaves
  the attachments of whatever the database deletes in a cascade. Such a deletion
  is rare: Odoo refuses to delete a company that other modules' records hold,
  such as the internal project that ``hr_timesheet`` gives each company.
