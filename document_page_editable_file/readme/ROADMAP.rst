* A file inserted in the *Editables* tab belongs to the tab once the user who
  inserted it, or a system administrator, saves it there. A file inserted and
  then discarded stays an ordinary attachment of the document, or of the
  version, and every user who reads the document can download it.
* A user who reads the documents but is not in the group can still filter the
  documents by the text of their *Editables* through the API: Odoo 14 does not
  apply the groups of a field to a search filter. The user learns which
  documents match, but gets neither the field nor its files.
* The information inside the Word file, such as the author, the tracked changes
  or the comments, is not cleaned.
