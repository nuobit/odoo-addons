* Two changes at the same time, one that adds a document to a list and one that
  turns that document into a category, are both accepted, and the list is left
  with a category: until it is taken out of the list, every save that changes
  the list is refused. The form does not offer the change of type: only an
  import, the API or another module can make it.
* As with any many2many field, Odoo does not check that the user can read the
  record they link by its id. Through the API or an import, an editor can add a
  document they cannot read: it is not shown to them, but they learn whether
  the id belongs to a document, and that document cannot be turned into a
  category while it is in the list.
* A search on the list through the API tells a user that a document has related
  documents they cannot read and, by their id, which ones. Their names and
  contents stay hidden.
* The arrow opens nothing on a document whose form cannot be saved: the form
  requires the content and the name and summary of the current version, and
  the arrow saves the form first. With *Document Page Approval* the three stay
  empty until a version is approved: while the first change waits for
  approval, or after it is cancelled. The approval module's own *Change
  Requests* button fails there the same way. With or without that module, a
  current version saved with no name or summary, through an import or the API,
  does the same.
