By default, the OCA module ``document_page`` exposes a search field on the
``content`` of a page that only matches against the page HTML body. When users
attach files to a page (PDF, docx, xlsx, OpenDocument...), the text inside
those files is not reachable from that search even though Odoo's
``attachment_indexation`` already extracts and stores it in
``ir.attachment.index_content``.

This module extends the ``content`` search of ``document.page`` so that the
same query also matches the indexed content of the files embedded in the page
body (``ir.attachment`` referenced from the HTML of the page).

Behavior:

* The existing search box keeps working exactly as before.
* For text operators (``like``, ``ilike``, ``=like``, ``=ilike``) the search
  domain is widened to also match attachments whose indexed content contains
  the query.
* Only attachments actually referenced in the current page HTML (via
  ``/web/content/<id>`` or ``/web/image/<id>``) are considered. Attachments
  that were removed/replaced in the editor but left behind by Odoo (which never
  deletes the underlying ``ir.attachment``) are ignored, so a stale file no
  longer produces false matches. Files attached only through the chatter are
  not searched, as they are not part of the page body.
* For other operators (``=``, ``!=``, ``not ilike``, etc.) the original
  behavior is preserved untouched: combining attachment matches with negation
  would change the semantics of the original search.
* No new fields, views or menus are added; the existing OCA search box is the
  single entry point.

Prerequisites:

* ``attachment_indexation`` must be installed (declared as a dependency).
* ``pdfminer.six`` must be available system-wide for PDF text extraction;
  otherwise PDFs uploaded to a page remain unindexed and cannot be matched.
* Attachments uploaded before installing ``attachment_indexation`` /
  ``pdfminer.six`` are not retroactively indexed; rewriting their content
  triggers re-indexation.
* Scanned PDFs (image-only) yield no extractable text and are not matched.
