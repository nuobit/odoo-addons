By default, the OCA module ``document_page`` exposes a search field on the
``content`` of a page that only matches against the page HTML body. When users
attach files to a page (PDF, docx, xlsx, OpenDocument...), the text inside those
files is not reachable from that search even though Odoo's
``attachment_indexation`` already extracts and stores it in
``ir.attachment.index_content``.

This module extends the ``content`` search of ``document.page`` so that the same
query also matches the indexed text of the files attached to the page.

Behavior:

* The existing search box keeps working exactly as before.
* For text operators (``like``, ``ilike``, ``=like``, ``=ilike``) the search
  domain is widened to also match pages that have an attachment
  (``ir.attachment`` with ``res_model=document.page``) whose indexed content
  contains the query. The page is resolved from the attachment's ``res_id``.
* For other operators (``=``, ``!=``, ``not ilike``, etc.) the original behavior
  is preserved untouched: combining attachment matches with equality or negation
  would change the semantics of the original search.
* No new fields, views or menus are added; the existing OCA search box is the
  single entry point.

Scope:

* Any file attached to the page is searchable, whether embedded in the body or
  attached through the chatter. The match relies on the native ``res_model`` /
  ``res_id`` link that Odoo maintains, not on parsing the page HTML, so it is
  unaffected by modules that rewrite the body links (e.g.
  ``document_page_distribution_download_log``).
* A file uploaded into a page that has not been saved yet gets ``res_id=0`` and
  cannot be mapped back to a page, so it is not matched until that link is set.

Prerequisites:

* ``attachment_indexation`` must be installed (declared as a dependency).
* ``pdfminer.six`` must be installed in Odoo's Python environment (declared as an
  external dependency, so the module will not install without it) and Odoo must
  be restarted after installing it; otherwise PDFs attached to a page remain
  unindexed and cannot be matched.
* Attachments uploaded before installing ``attachment_indexation`` /
  ``pdfminer.six`` are not retroactively indexed; use the post-migration
  reindexing below to index them.
* Scanned PDFs (image-only) yield no extractable text and are not matched.

Post-migration reindexing:

When pages and their files are imported in bulk (a migration), the attachments
may be created with their ``index_content`` left empty, so the search cannot
match them yet. Recompute it once, reusing Odoo's own indexing and without
rewriting the page content (so no new revision is created), from a shell::

    odoo-bin shell -c <odoo.conf> -d <database>
    >>> env["document.page"].reindex_attachment_content(
    ...     batch_size=500, only_missing=True)
    >>> env.cr.commit()

``batch_size`` caps how many attachments are processed per run (re-run until
``processed`` is ``0``); ``only_missing`` limits the work to attachments whose
``index_content`` is still empty. The call returns a summary
``{"processed", "skipped", "no_text"}``; ``no_text`` lists the ``(id, name)`` of
attachments that yielded no extractable text (scanned PDFs, or PDFs indexed
without ``pdfminer.six``).
