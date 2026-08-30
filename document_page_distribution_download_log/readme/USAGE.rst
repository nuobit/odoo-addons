.. important::

   Install this module **before** the controlled document versions you want to
   track are authored. The version-aware download link is written into a
   version's content the moment that content is **saved with this module
   installed**. A version whose content was saved *before* the install keeps its
   raw ``/web/content`` link and is therefore **not tracked** until its next
   revision.

#. Install this module on top of *Document Page Distribution*: it adds the
   download evidence on top of the person + version coverage.
#. Make sure your controlled documents have a Security group and have been
   distributed at least once (which creates the coverage lines).
#. Edit a document page and insert a single document link (one file) in its
   content. Saving content with more than one document link is rejected.
   Insert the file with the page editor, which binds it to the page: a file
   the recipient cannot read (e.g. uploaded outside the editor and bound to
   nothing) answers 404 and no download evidence is recorded.
#. On save, the document link is rewritten to a controlled, version-aware
   download URL.
#. When a covered recipient opens the link, the access is logged against their
   coverage line for that exact version. Opening it again adds a new evidence
   row and updates the last download date, keeping the first one. Opening the
   link of an old version is always imputed to that old version.
#. If a user with read access but without a coverage line opens the link, the
   file is served but no evidence is recorded (coverage stays owned by the
   distribution module).
#. In the *Distribution* tab of the document, each recipient row shows whether
   they downloaded the current version, with a button opening the full download
   detail (date, user, file), next to the send detail.

.. note::

   Uninstalling this module does **not** restore the original ``/web/content``
   links in versions saved while it was installed: their stored content keeps
   the rewritten tracking links, which stop working once the module (and its
   download route) is gone. Re-insert the document link manually on the next
   revision if you uninstall.
