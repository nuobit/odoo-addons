Keeps the editable files of each version of a document of the Knowledge
application, such as the Word file its PDF comes from, for the Knowledge
editors.

* Each version of a document has a list of editable files, of any kind, in an
  *Editables* tab of its form: there they are uploaded, replaced, renamed,
  sorted and removed.
* The document shows the editable files of the version it shows, in an
  *Editables* tab right after *History*, with a button that opens that version.
* A save that changes the content of the document makes a new version, which
  starts with the editable files of the version the document showed; the
  earlier version keeps its own. A duplicated version keeps the files of the
  version it is made from, or, given another document, starts with the files
  that document shows; a duplicated document starts without editable files.
* The editable files of a version change only while the document shows that
  version, so the earlier versions keep theirs as they were. Where
  ``document_page_approval`` is installed, ``document_page_editable_file_approval``
  makes them follow its change requests.
* Only the Knowledge editors, and the managers through them, see those tabs,
  download the files and search by them. A user who edits a document without
  being an editor keeps its files on the new version without seeing them. The
  files are neither attachments of the document nor of the version: the
  chatter does not show them, and a user who cannot read them does not find
  them among the attachments.
