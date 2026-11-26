* ``document_page_access_group`` limits who reads a document, not who reads its
  versions: a Knowledge editor outside the groups of a document's *Security*
  tab still reads and changes the editable files of its versions.
* Through the API, a write that moves an editable file into a version of another
  company and sets its file in the same call, with ``bin_size`` in its context,
  is not refused: Odoo serves the file from its cache to the check that refuses
  such a move. The screens never send such a call.
* Through the API, a save of a document that gives its *Editables* list as
  ``False`` or ``None``, Odoo's ways to remove every file, leaves its files as
  they are; the rest of the save is kept.
* Through the API, a save of a document that changes its content and gives its
  *Editables* list as a plain list of ids fails.
* Through the API, a save of a document that changes its content and its
  *Editables* list, with a context that gives the new version files of its own
  (``default_editable_file_ids``), changes those files instead of the copies of
  the files it names: each file is paired with its copy by their order, and the
  pairs are not checked. When the context gives fewer files than the version
  shown has, a file the save names that is left without a pair makes the save
  fail: it is still a file of the earlier version, which can no longer change.
* Through the API, a version duplicated into another document (``copy`` with
  the ``page_id`` of another document) starts with the editable files of the
  version that document shows, not with those of the version duplicated; which
  of the two it should take is not decided yet. The screens' *Duplicate* keeps
  the version's document.
* Server code that creates a version with several versions as
  ``editable_files_origin`` in its context is not refused: the new version
  starts with the files of all of them when they all belong to its document.
* The information inside a file, such as the author, the tracked changes or the
  comments of a Word file, is not cleaned.
* Uninstalling the module deletes every editable file: Odoo deletes the
  attachments of the models it removes.
* Deleting a company deletes its documents, their versions and their editable
  files, but not the attachments that hold the files' contents, as Odoo leaves
  the attachments of whatever the database deletes in a cascade. Such a deletion
  is rare: Odoo refuses to delete a company that other modules' records hold,
  such as the internal project that ``hr_timesheet`` gives each company.
