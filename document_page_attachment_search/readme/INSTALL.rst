* ``attachment_indexation`` must be installed (declared as a dependency).
* ``pdfminer.six`` must be installed in Odoo's Python environment (declared as an
  external dependency, so the module will not install without it) and Odoo must
  be restarted after installing it; otherwise PDFs attached to a page remain
  unindexed and cannot be matched.
* Attachments uploaded before installing ``attachment_indexation`` /
  ``pdfminer.six`` are not retroactively indexed; use the post-migration
  reindexing of the usage section to index them.
